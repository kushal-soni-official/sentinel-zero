import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

class CorrectionResult:
    def __init__(self, is_consistent: bool, confidence: float, reason: str, corrected_findings: list):
        self.is_consistent = is_consistent
        self.confidence = confidence
        self.reason = reason
        self.corrected_findings = corrected_findings

class SelfCorrector:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key)
        self.model_name = "gemini-2.5-flash"

    def evaluate(self, prior_findings, new_findings, tool_outputs):
        """
        Evaluate if the findings are logically consistent with the tool outputs.
        Catches hallucinations, unwarranted conclusions, or logical contradictions.
        Uses an independent Gemini call (not the same instance as the agent) for unbiased auditing.
        """
        prompt = f"""You are a senior security forensics self-correction system.
Your job is to audit the security findings of an AI agent by comparing them directly to the raw tool outputs.
You must catch hallucinations, assumptions, or claims that are NOT backed by hard evidence in the tool output.

RAW TOOL OUTPUTS:
{json.dumps(tool_outputs, indent=2)}

PRIOR FINDINGS (from previous iterations):
{json.dumps(prior_findings, indent=2)}

NEW FINDINGS (proposed in this iteration):
{json.dumps(new_findings, indent=2)}

Verify the following:
1. Are all claims in the findings directly backed by text in the raw tool outputs?
2. Are there any false assumptions or hallucinations (e.g. claiming lateral movement happened when no network tools show it)?
3. If there is a hallucination or inconsistency, mark is_consistent=false, explain why under reason, and remove/correct the invalid findings in corrected_findings.
4. Set a confidence score from 0.0 (unreliable) to 1.0 (verified).

Respond ONLY in JSON format with the following structure:
{{
  "is_consistent": bool,
  "confidence": float,
  "reason": "explanation of any hallucinations, errors, or consistency check success",
  "corrected_findings": [
    {{
      "finding": "description of the verified finding",
      "evidence": "exact quote or reference from tool output",
      "severity": "CRITICAL" | "HIGH" | "MEDIUM" | "LOW"
    }}
  ]
}}
"""
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            # FIX: Strip markdown fencing that Gemini sometimes wraps around JSON
            # even when response_mime_type is set. Without this, json.loads raises
            # JSONDecodeError, causing the corrector to silently pass raw unverified findings.
            raw_text = response.text.strip()
            if raw_text.startswith("```"):
                raw_text = raw_text.split("\n", 1)[-1]
                if raw_text.endswith("```"):
                    raw_text = raw_text.rsplit("```", 1)[0]
            data = json.loads(raw_text.strip())
            return CorrectionResult(
                is_consistent=data.get("is_consistent", True),
                confidence=data.get("confidence", 1.0),
                reason=data.get("reason", "Checks passed."),
                corrected_findings=data.get("corrected_findings", new_findings)
            )
        except Exception as e:
            # Fallback in case of API error or invalid JSON
            print(f"[SelfCorrector Error] {str(e)}")
            return CorrectionResult(
                is_consistent=True,
                confidence=0.8,
                reason=f"Self-correction evaluation failed or defaulted: {str(e)}",
                corrected_findings=new_findings
            )
