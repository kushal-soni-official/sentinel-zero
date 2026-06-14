# Sentinel Zero — Project Description
### SANS Institute FIND EVIL! Hackathon 2026 · Submission Component #4

---

## What It Does

Sentinel Zero is an **autonomous AI security agent** that operates in two modes:

1. **Splunk Mode** — Connects to Splunk SIEM and autonomously triages live security alerts. The agent ranks alerts by severity, investigates the underlying threat chain using MCP-exposed tools, self-corrects its own reasoning, and produces a structured Incident Response Runbook in seconds.

2. **SIFT Forensics Mode** — Connects to a custom-built SIFT MCP Server (exposing `fls`, `volatility3`, and `grep` in read-only mode) to perform autonomous digital forensic analysis on disk images and memory dumps. The agent reconstructs attack timelines, identifies malware indicators, and generates remediation playbooks while maintaining absolute evidence integrity.

**Core value proposition:** The average SOC analyst reviews 50–100 alerts per day against a daily volume of 500–5,000. Sentinel Zero covers them all — instantly.

---

## How We Built It

### Architecture

Sentinel Zero uses a unified FastAPI backend (`app.py`) with Server-Sent Events (SSE) for real-time streaming of agent reasoning to the frontend dashboard.

**The agent core** (`core/agent.py`) runs an autonomous loop powered by **Google Gemini (gemini-2.5-flash)**:
1. Receives task + security context
2. Calls tools via the **Model Context Protocol (MCP)** through a local MCP client dispatcher
3. Receives structured tool outputs and formulates findings
4. Passes all findings through the **Self-Correction Engine** (`core/self_correct.py`)
5. Repeats (up to 5 iterations) until confidence > 85% or investigation is complete
6. Generates a final **Incident Response Runbook** in Markdown

**The Self-Correction Engine** is a second independent Gemini call that acts as a forensic auditor — it compares every proposed finding against the raw tool outputs and explicitly removes or flags any claim not supported by hard evidence. This catches hallucinations before they enter the final report.

**The MCP Layer** uses two connectors:
- **Custom SIFT MCP Server** (`sift_mcp_server/server.py`) — a FastMCP server we built exposing three read-only SIFT forensic tools. This approach was chosen because the SANS hackathon judging guidelines award maximum points for teams that build their own MCP server (Architectural Approach #2).
- **Splunk MCP Client** (`splunk_config/mcp_client_config.json`) — config for connecting to Splunk's official MCP server for the Splunk track.

**The Frontend** is a glassmorphic cyberpunk dashboard with scroll-driven storytelling (400vh scroll depth), a 3D canvas particle system, and a frame-scrubbing sequence player. The SSE log stream prints every agent action in real time.

### Tech Stack
- **AI Model:** Google Gemini 2.5 Flash (via `google-generativeai` SDK)
- **Agent Protocol:** Model Context Protocol (MCP) — FastMCP server
- **Backend:** FastAPI + uvicorn with SSE streaming
- **Frontend:** Vanilla HTML/CSS/JS with Canvas 2D API
- **Forensic Tools:** `fls` (Sleuth Kit), `volatility3`, `grep` (via subprocess, read-only)
- **Data:** Splunk CIM-schema mock alerts + SANS-style forensic mock datasets

---

## Challenges We Faced

1. **Gemini JSON hallucination in Self-Correction:** The model would occasionally wrap its structured JSON output in markdown fences (` ```json ``` `) even when `response_mime_type="application/json"` was set, causing `JSONDecodeError` and silently bypassing the correction layer. Fixed by adding a fence-stripping sanitizer before `json.loads()`.

2. **Double-serialization in tool outputs:** The MCP client returned JSON strings, but the agent stored them raw and then re-serialized with `json.dumps()`, producing double-escaped output that confused the model's context window. Fixed by parsing JSON strings back to dicts at the dispatcher boundary.

3. **Context window overflow:** `fls` and `volatility3` return thousands of lines. Passing full raw outputs into every Gemini prompt was hitting token limits and degrading reasoning quality. Fixed by capping tool output at 1,000 characters per entry in the runbook generation step.

4. **Thread-to-async bridge:** The agent runs in a daemon thread (to keep FastAPI non-blocking), but SSE event queuing requires asyncio. Solved with `loop.call_soon_threadsafe()` to safely push events from the thread into the async queue.

---

## What We Learned

- **Architectural security is more convincing than prompt security.** By exposing only read-only tool functions via MCP, the AI physically cannot destroy evidence — there is no destructive path in the code, not just in the system prompt.
- **LLM self-correction works — but it needs a second independent call.** Using the same model instance to both generate and validate findings creates a confirmation bias loop. Using a separate Gemini call as the auditor, with explicit instructions to find and remove claims not in the tool output, catches real hallucinations.
- **Token framing matters for autonomous loops.** Passing full raw forensic tool output to every iteration creates diminishing returns. Summarizing to the most relevant 1,000 characters keeps the model focused on what matters.

---

## What's Next

1. **Live Splunk integration** — replace mock alerts with real Splunk Enterprise search queries via the Splunk SDK and the official Splunk MCP Server.
2. **Multi-agent triage** — spawn parallel sub-agents for concurrent alert investigation using a CrewAI or AutoGen framework layer.
3. **MITRE ATT&CK mapping** — automatically tag every finding with a MITRE technique ID and query the ATT&CK Navigator API to enrich the runbook.
4. **Case management output** — push the final runbook and IOC list to JIRA, ServiceNow, or TheHive via webhook.
5. **Air-gapped mode** — swap Gemini for a local Ollama model (e.g., Llama 3.1 70B) for deployment on isolated SIFT workstations without internet access.

---

*Sentinel Zero · [github.com/kushal-soni-official/sentinel-zero](https://github.com/kushal-soni-official/sentinel-zero) · SANS Institute FIND EVIL! Hackathon 2026 · MIT License*
