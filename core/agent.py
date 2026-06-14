import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv
from core.logger import AgentLogger
from core.self_correct import SelfCorrector

load_dotenv()

class SentinelZeroAgent:
    def __init__(self, mcp_client=None, mode="splunk"):
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key)
        self.model_name = "gemini-2.5-flash"
        self.mcp_client = mcp_client
        self.logger = AgentLogger()
        self.corrector = SelfCorrector()
        self.mode = mode
        self.max_iterations = 5  # Safety cap for autonomous loop

    def analyze(self, task, context_data):
        self.logger.start_session(task)
        iteration = 0
        findings = []
        tool_outputs = []
        correction = None

        self.logger.log(f"Starting security triage in {self.mode.upper()} mode.")

        while iteration < self.max_iterations:
            iteration += 1
            self.logger.log(f"[ITERATION {iteration}] Analyzing data...")

            # Build detailed prompt for the agent
            prompt = self._build_prompt(task, context_data, findings, tool_outputs)

            # Fetch tools available from the MCP client
            gemini_tools = []
            if self.mcp_client:
                gemini_tools = self.mcp_client.get_gemini_tools()

            # Execute Gemini analysis (new google.genai SDK)
            response = None
            try:
                if gemini_tools:
                    response = self.client.models.generate_content(
                        model=self.model_name,
                        contents=prompt,
                        config=types.GenerateContentConfig(tools=gemini_tools)
                    )
                else:
                    response = self.client.models.generate_content(
                        model=self.model_name,
                        contents=prompt
                    )
            except Exception as api_err:
                self.logger.log(f"[API ERROR] Gemini API call failed on iteration {iteration}: {api_err}")
                break

            if response is None:
                break

            # Check if Gemini wants to call tools (Function Calls)
            has_tool_calls = False
            new_findings = []

            # Extract function calls defensively from the new SDK response structure
            if response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if candidate.content and candidate.content.parts:
                    for part in candidate.content.parts:
                        if hasattr(part, 'function_call') and part.function_call:
                            has_tool_calls = True
                            tool_name = part.function_call.name
                            tool_args = dict(part.function_call.args) if part.function_call.args else {}

                            self.logger.log_tool_call(tool_name, tool_args)

                            # Call tool via MCP Client
                            if self.mcp_client:
                                raw_result = self.mcp_client.call_tool(tool_name, tool_args)
                            else:
                                raw_result = json.dumps({"error": "MCP Client not configured."})

                            # FIX: Parse JSON string back to dict to prevent double-serialization
                            try:
                                result = json.loads(raw_result) if isinstance(raw_result, str) else raw_result
                            except (json.JSONDecodeError, TypeError):
                                result = {"raw": str(raw_result)}

                            self.logger.log_tool_result(tool_name, result)

                            tool_outputs.append({
                                "tool": tool_name,
                                "arguments": tool_args,
                                "output": result
                            })
                            new_findings.append({
                                "finding": f"Analyzed using {tool_name}",
                                "evidence": str(result)[:300],
                                "severity": "INFO"
                            })

            # If Gemini didn't make tool calls but generated text, parse it
            if not has_tool_calls:
                try:
                    text_response = response.text
                except (ValueError, AttributeError):
                    text_response = "No text content returned (possibly blocked or empty response)."

                self.logger.log("No further tool calls requested. Finalizing findings.")
                new_findings.append({
                    "finding": "Analysis Summary",
                    "evidence": text_response,
                    "severity": "HIGH"
                })

            # SELF-CORRECTION LOOP (Crucial for SANS Criterion #1)
            correction = self.corrector.evaluate(findings, new_findings, tool_outputs)
            self.logger.log_correction(correction.reason, correction.corrected_findings, correction.confidence)

            # Update findings
            findings = correction.corrected_findings

            # Break if consistent and confidence is high
            if correction.is_consistent and correction.confidence > 0.85 and not has_tool_calls:
                self.logger.log(f"[DONE] Investigation completed in {iteration} iterations.")
                break
            elif not has_tool_calls:
                self.logger.log(f"[WARNING] Inconsistent findings detected, running correction round.")

        # Generate the final Incident Response Runbook
        runbook = self._generate_runbook(task, findings, tool_outputs)

        return {
            "mode": self.mode,
            "task": task,
            "findings": findings,
            "tool_outputs": tool_outputs,
            "runbook": runbook,
            "iterations": iteration,
            "confidence": correction.confidence if correction else 0,
            "execution_log": self.logger.get_log()
        }

    def _build_prompt(self, task, context, prior_findings, tool_outputs):
        # Truncate large tool outputs to avoid context window overflow on multi-iteration loops
        safe_tool_outputs = []
        for t in tool_outputs:
            entry = dict(t)
            if isinstance(entry.get("output"), dict):
                raw = entry["output"].get("output", "")
                if isinstance(raw, str) and len(raw) > 2000:
                    entry["output"] = dict(entry["output"])
                    entry["output"]["output"] = raw[:2000] + "... [TRUNCATED]"
            safe_tool_outputs.append(entry)

        return f"""You are Sentinel Zero, an autonomous incident response AI security agent.
Your objective is to investigate the security incident, identify compromise indicators, and create an Incident Response plan.

TARGET TASK:
{task}

INCIDENT CONTEXT:
{json.dumps(context, indent=2)}

PRIOR FINDINGS (Verify these for inconsistencies, logical flaws, or lack of evidence):
{json.dumps(prior_findings, indent=2)}

RAW TOOL OUTPUTS OBTAINED SO FAR:
{json.dumps(safe_tool_outputs, indent=2)}

Security Constraints:
1. NEVER run destructive commands (You are restricted to read-only tools).
2. Every finding MUST have corresponding evidence in the tool output.
3. If a prior finding is NOT backed by tool output, explicitly list it as a hallucination/error and state that it was removed.
4. Keep digging if there are critical security questions unanswered.

Select from the available tools to proceed with your investigation, or summarize your final findings and stop calling tools when you have sufficient evidence.
"""

    def _generate_runbook(self, task, findings, tool_outputs):
        # Truncate large tool outputs to prevent context window exhaustion
        truncated_outputs = []
        for t in tool_outputs:
            entry = dict(t)
            if isinstance(entry.get("output"), dict):
                raw = entry["output"].get("output", "")
                if isinstance(raw, str) and len(raw) > 1000:
                    entry["output"] = dict(entry["output"])
                    entry["output"]["output"] = raw[:1000] + "... [TRUNCATED FOR RUNBOOK]"
            truncated_outputs.append(entry)

        prompt = f"""You are Sentinel Zero. Generate a professional Incident Response Runbook based on the investigation findings.
Keep it structured, actionable, and formatted in Markdown.

TASK INVESTIGATED:
{task}

VERIFIED FINDINGS:
{json.dumps(findings, indent=2)}

EVIDENCE GATHERED (summarized):
{json.dumps(truncated_outputs, indent=2)}

Include the following sections in your Runbook:
1. Executive Summary
2. Detailed Threat Analysis (Impact, compromised assets)
3. Step-by-Step Remediation Plan (Containment, Eradication, Recovery)
4. Lessons Learned & Hardening Recommendations
"""
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return response.text
        except Exception as e:
            return f"# Incident Response Runbook\n\nFailed to generate Runbook: {str(e)}"
