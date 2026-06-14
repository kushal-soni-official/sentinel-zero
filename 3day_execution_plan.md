# ⚡ ZERO-COST 3-DAY EXECUTION PLAN
## Splunk ($20K) + Findevil ($22K) — June 13–15, 2026

> **Current time:** June 13, 12:19 AM PDT
> **Splunk deadline:** June 15, 9:00 AM PDT (~57 hours)
> **Findevil deadline:** June 15, 8:45 PM PDT (~68 hours)

---

## THE CORE INSIGHT: ONE PROJECT, TWO SUBMISSIONS

You're building **one AI security agent** with MCP integration.
- For **Splunk** → it monitors Splunk security alerts
- For **Findevil** → it triages SIFT forensic case data

**Same codebase. Different connectors. Submitted to both.**

*(Note: Deep technical details, architecture diagrams, and full code snippets have been moved to the `project_names_and_overview.md` file to keep this plan simple.)*

---

## ZERO-COST TOOL STACK (100% Free)

| Tool | Purpose | Free Plan |
|---|---|---|
| **GitHub** | Code repo (required by both) | Unlimited public repos |
| **Gemini API (Google AI Studio)** | The AI brain | Free: 1,500 req/day, 1M tokens/day |
| **Splunk Free Trial** | Splunk instance | 60-day free, 500MB/day |
| **SIFT Workstation** | Findevil platform | 100% free, open source |
| **Protocol SIFT** | MCP on SIFT | 100% free, open source |
| **Python** | Code language | Free |
| **FastAPI / MCP Python SDK** | Build MCP servers | Free via pip |
| **YouTube** | Demo video hosting | Free |
| **OBS Studio** | Screen recording | Free at obsproject.com |
| **VS Code** | Code editor | Free |
| **Google Colab** | Cloud compute if needed | Free GPU |

> Get free Gemini API key at: https://aistudio.google.com/app/apikey

---

## HOUR-BY-HOUR SCHEDULE

### DAY 1 — June 13 (Saturday) — SETUP + BUILD CORE

**00:00–01:00 — Setup Accounts (do in parallel browser tabs)**
- Tab 1: Get FREE Gemini API key (aistudio.google.com/app/apikey)
- Tab 2: Create Splunk free account (splunk.com/en_us/form/sign-up.html)
- Tab 3: Create public GitHub repo
- Tab 4: START SIFT DOWNLOAD NOW (sans.org/tools/sift-workstation) — *It's a large file!*

**01:00–02:00 — GitHub Repo Structure**
- Create folders: `core`, `splunk_connector`, `sift_connector`, `demo_data`
- Create empty files: `README.md`, `accuracy_report.md`, `LICENSE`
- Initialize git and push to GitHub

**02:00–04:00 — Build Core Agent (Gemini-powered)**
- Implement the main Gemini agent loop (`core/agent.py`)
- Implement the execution logger (`core/logger.py`)
- Implement the self-correction logic (`core/self_correct.py`)

**04:00–06:00 — Build Splunk Connector**
- Implement Splunk API wrappers (`splunk_connector/alert_tools.py`)
- Set up demo data JSON for local testing without needing a full Splunk instance.

**06:00–09:00 — SLEEP** 😴

**09:00–12:00 — Build SIFT Connector**
- Implement read-only SIFT tool wrappers (`sift_connector/sift_tools.py`)
- Setup the MCP server for SIFT (`sift_connector/mcp_server.py`)

**12:00–15:00 — Wire Together + Test**
- Run test scripts for both Splunk and SIFT modes using the demo data.

---

### DAY 2 — June 14 (Sunday) — FINDEVIL POLISH + VIDEOS

**09:00–12:00 — SIFT VM Setup**
- Import SIFT OVA into VirtualBox/VMware
- Install Protocol SIFT inside the VM
- Clone repo into the VM and test execution against sample case data

**12:00–14:00 — Write Accuracy Report**
- Document false positives, missed artifacts, and self-correction wins.
- Be honest — judges reward transparency over fake perfection.

**14:00–16:00 — Architecture Diagram**
- Use app.diagrams.net (draw.io) to draw the system architecture.
- Export as PNG and save to repo root as `architecture_diagram.png`.

**16:00–19:00 — Record Demo Videos**
- **Splunk Video (STRICTLY under 3 mins):** State the problem -> Show agent running -> Show MCP tool calls in terminal -> Show final result.
- **Findevil Video (max 5 mins):** State the problem -> Show agent analyzing case data -> Show the AI catching its own hallucination -> Show execution logs.
- Upload both to YouTube (Unlisted is fine).

**19:00–21:00 — Write READMEs + Push Code**
- Document setup instructions and push all final changes to GitHub.

---

### DAY 3 — June 15 (Monday) — SUBMIT BOTH

**BY 8:30 AM PDT — Submit Splunk (deadline 9:00 AM PDT)**
- Fill out Devpost page with project name, description, YouTube link, GitHub URL.
- Ensure video is under 3 minutes.
- Select the "Security" track.

**BY 6:00 PM PDT — Submit Findevil (deadline 8:45 PM PDT)**
- Ensure all 8 required components are present:
  1. [ ] GitHub repo URL (public)
  2. [ ] Demo video link (shows self-correction)
  3. [ ] Architecture diagram (`architecture_diagram.png` in repo)
  4. [ ] Written description on Devpost
  5. [ ] Dataset documentation (inside accuracy report)
  6. [ ] Accuracy report (`accuracy_report.md` in repo)
  7. [ ] Try-it-out instructions (in README)
  8. [ ] Execution logs (`execution_log.json` in repo)
- Submit on Devpost.

---

## ZERO-COST EMERGENCY OPTIONS

**If Splunk setup is too slow:**
Use demo mode only — hardcode sample alerts data. Add note: "Demo mode available for judges without local Splunk."

**If SIFT VM is too slow:**
Run against sample output files simulating what SIFT tools return.

**If you need free cloud compute:**
Use Google Colab (free GPU) — run your agent there and screen record it.

---

## TIME BUDGET

| Task | Time |
|---|---|
| Setup accounts | 1h |
| Core agent code | 2h |
| Splunk connector | 2h |
| SIFT connector | 3h |
| Testing + fixes | 3h |
| Architecture diagram | 1h |
| Demo videos (×2) | 3h |
| READMEs + reports | 2h |
| Submissions | 1h |
| **TOTAL WORK** | **18 hours** |

18 hours across 57–68 calendar hours = very sustainable.
