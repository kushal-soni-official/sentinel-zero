# Sentinel Zero — Autonomous Security Triage & Forensic Agent
### Made during Splunk Agentic Ops Hackathon &amp; SANS FIND EVIL! Hackathon Submission

[![GitHub Repo](https://img.shields.io/badge/GitHub-sentinel--zero-blue?logo=github)](https://github.com/kushal-soni-official/sentinel-zero)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://python.org)
[![Powered by Gemini](https://img.shields.io/badge/AI-Gemini%202.5%20Flash-orange?logo=google)](https://ai.google.dev)

Sentinel Zero is an autonomous AI incident response agent designed to triage security alerts and perform forensic investigation. By leveraging the Model Context Protocol (MCP) and Google Gemini, the agent can connect to live Splunk feeds or audit SANS SIFT forensic images, securely run read-only analysis tools, self-correct its own hallucinations, and compile detailed remediation runbooks in seconds.

---

## 🌐 Live Deployment (Vercel + Hugging Face Spaces)
The project utilizes a dual-hosting architecture for maximum performance and zero timeouts:
* **Frontend (Vercel):** The premium glassmorphic UI (`frontend/`) is deployed as a pure-static site on Vercel for instant load times and smooth 60fps animations.
* **Backend (Hugging Face Spaces):** The FastAPI server (`app.py`), Gemini agent, and MCP tools run in a dedicated Docker container on Hugging Face Spaces. This entirely bypasses Vercel's 10-second serverless timeout, allowing long-running forensic investigations and real-time SSE streaming.

🔗 **Live Demo:** [https://sentinel-zero.vercel.app](https://sentinel-zero.vercel.app/)

> **Note:** The frontend automatically detects if it's running locally or on Vercel. On Vercel, it routes all API calls to the Hugging Face backend. Locally, it routes to your local Python server.

---

## 🛠️ Architecture & System Structure

The system uses a unified codebase with distinct mode connectors:
* **Live Threat Intel (Zero Hallucination)**: The agent connects to the live **AlienVault OTX API** to verify malware hashes (like WannaCry) and IP addresses (like Tor exit nodes) in real-time.
* **Splunk Mode**: Triage security alerts, investigate system states, and compile containment playbooks.
* **SIFT Mode**: Connect to a custom SIFT MCP Server, use forensic tools (`fls`, `volatility3`, `grep`), detect compromises, and maintain absolute evidence integrity.

```text
sentinel-zero/
├── core/
│   ├── agent.py               # Gemini-powered autonomous agent loop
│   ├── self_correct.py        # Self-correction logic (catches hallucinations)
│   ├── logger.py              # Timestamped execution logger (Findevil audit trail)
│   └── mcp_client.py          # Local MCP client tool-binding dispatcher
├── sift_mcp_server/
│   ├── server.py              # SIFT FastMCP server (exposing forensic commands)
│   └── tools.py               # Forensics tools wrappers (including live AlienVault OTX)
├── splunk_config/
│   └── mcp_client_config.json # Config to connect client to Splunk's official server
├── demo_data/                 # High-fidelity mock alerts & forensics dumps
│   ├── mock_alerts.json       # Splunk security events (with real-world malicious IPs)
│   ├── mock_filesystem.txt    # Mock fls tool directory listing (with WannaCry SHA256)
│   └── mock_volatility.txt    # Mock volatility process list output
├── hf_space/                  # Hugging Face Spaces deployment config
│   ├── Dockerfile             # Backend container definition
│   └── README.md              # HF Space YAML configuration
├── frontend/                  # Premium 60fps glassmorphic dashboard
│   ├── index.html             
│   ├── style.css              
│   └── app.js                 # Optimized requestAnimationFrame scrubbing logic
├── app.py                     # FastAPI web server and SSE event streamer
├── vercel.json                # Vercel deployment configuration (pure static)
├── requirements.txt           # Python library dependencies
├── accuracy_report.md         # SANS Findevil accuracy metrics
└── README.md                  # Setup and execution guide
```

---

## ⚡ Quick Start (Windows CMD)

Follow these steps to run Sentinel Zero locally.

### 1. Install Dependencies
Ensure you have Python 3.10+ installed. Run the following command in standard Windows Command Prompt (CMD) to install all required libraries:
```cmd
pip install -r requirements.txt
```

### 2. Set API Key Configuration
Create a `.env` file in the root directory (or edit the one created automatically) and add your Gemini API Key:
```env
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
PORT=8001
```

### 3. Start the Web Server
Launch the FastAPI backend and web server:
```cmd
python app.py
```

### 4. Access the Dashboard
Open your web browser and navigate to:
[http://localhost:8001](http://localhost:8001)

---

## 🧪 Try-It-Out Instructions (Findevil Component #7)

Sentinel Zero is designed to run with **zero external dependencies**. All forensic tool outputs fall back to high-fidelity mock data automatically when SIFT tooling is unavailable.

### Option A — Local Run (Windows)
```cmd
# 1. Clone the repository
git clone https://github.com/kushal-soni-official/sentinel-zero.git
cd sentinel-zero

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Configure API key (edit .env file)
echo GEMINI_API_KEY=YOUR_KEY_HERE > .env
echo PORT=8001 >> .env

# 4. Launch the dashboard (opens browser automatically)
run_dashboard.cmd
```

### Option B — Quick Manual Launch
```cmd
pip install -r requirements.txt
python app.py
# Then open http://localhost:8001 in your browser
```

### What to Expect
1. **Dashboard loads** — cyberpunk glassmorphic UI with scrollytelling animation.
2. **Splunk Mode** — Click **Triage All Alerts** to watch the agent investigate mock Splunk events via SSE stream.
3. **SIFT Mode** — Click **Run Forensic Audit** to watch tool calls, self-correction, and runbook generation.
4. **Self-Correction Panel** — Watch the AI catch and remove its own hallucinations in real time.
5. **Runbook** — Final Markdown IR plan renders and is copyable to clipboard.

---

## 🚀 How to Triage and Investigate

### 1. Splunk Security Triage Mode
* Select the **Splunk Triage** tab in the dashboard.
* You will see live alerts fetched from `demo_data/mock_alerts.json` (such as Ransomware, Exfiltration, or Web Shell drops).
* Click **Triage All Alerts**.
* The console will stream the agent's step-by-step investigation, showing how it reviews command line parameters and flags threats.

### 2. SIFT Forensic Studio Mode
* Select the **SIFT Forensics** tab in the dashboard.
* Review the disk and memory images loaded for analysis.
* Click **Run Forensic Audit**.
* The console will stream tool calls mimicking `fls` (filesystem scan) and `volatility3` (memory process scan).
* The **Self-Correction Inspector** will activate, showing how the agent catches its own logical jumps or false positive assumptions and repairs them before submitting the report.
* A detailed, copyable Markdown **Incident Response Runbook** will render at the bottom of the screen when completed.

---

## 🔒 Security Boundaries & Evidence Integrity
Sentinel Zero is built to conform to the strict security constraints of forensic audits:
* **Architectural Read-Only**: The tools exposed via `sift_mcp_server/tools.py` contain no data-modifying arguments. The agent physically cannot run a command that modifies the system or case logs.
* **Hash Integrity**: Forensic analyses are run on read-only copies of images. Original hashes (MD5/SHA256) are validated at start and completion to verify evidence integrity.
* **Perfect Audit Trail**: The backend records all actions in `execution_log.json` with milliseconds, tool parameters, and response states for complete compliance tracking.

---

## 📊 Dataset Documentation (Findevil Component #5)

All testing was conducted against the following datasets:

| Dataset | Source | Description |
|---|---|---|
| `mock_alerts.json` | Synthetic (Splunk-format) | 5 high-fidelity simulated Splunk security events including ransomware, web shell, and data exfiltration alerts. Mirrors real Splunk CIM schema. |
| `mock_filesystem.txt` | SANS SIFT sample (sanitized) | Simulated `fls` timeline output from a Windows 10 DFIR case. Contains registry hives, suspicious temp binaries, and bat/ps1 scripts. |
| `mock_volatility.txt` | SANS SIFT sample (sanitized) | Simulated `volatility3 windows.pslist` output showing injected `svchost32.exe` process with anomalous parent PID. |

**Data Integrity:** All mock data is static and read-only. No live forensic images are included in the repository. When live SIFT tools (`fls`, `volatility`) are detected on the host system, the agent automatically switches to live analysis mode.

**Evidence Chain:** Every tool invocation is logged in `execution_log.json` with:
- ISO 8601 timestamp (microsecond resolution)
- Tool name and exact arguments passed
- Full raw output returned
- Self-correction audit results

---

## 📜 License
MIT License — See [LICENSE](LICENSE) for details.
