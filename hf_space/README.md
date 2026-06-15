---
title: Sentinel Zero
emoji: 🛡️
colorFrom: cyan
colorTo: blue
sdk: docker
pinned: true
---

# 🛡️ Sentinel Zero — Autonomous Security Triage & Forensic Agent

FastAPI backend powering the **Sentinel Zero** autonomous AI incident-response agent.

**Dual Hackathon Submission:** [Splunk App Development Hackathon](https://splunk.devpost.com/) | [Finding Evil: Cybersecurity Hackathon](https://findevil.devpost.com/)

---

## 🌐 Live Frontend

👉 **[sentinel-zero.vercel.app](https://sentinel-zero.vercel.app/)** — Premium glassmorphic UI

---

## ⚙️ What This Backend Does

- Runs the **Gemini 2.5 Flash** autonomous agent loop (up to 5 iterations)
- Dispatches calls to **MCP tools** (SIFT forensics: `fls`, `volatility3`, `grep`)
- Integrates with **Splunk SIEM** alerts for live security triage
- Cross-validates findings against the **AlienVault OTX** live threat intel API
- Streams all agent reasoning via **Server-Sent Events (SSE)** to the frontend
- Rotates through a **pool of 5 Gemini API keys** automatically on quota exhaustion
- Catches and removes AI hallucinations via an independent **Self-Correction auditor**

---

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Serves frontend `index.html` |
| `/api/status` | GET | System health check — returns `{status: "active"}` |
| `/api/alerts` | GET | Returns Splunk mock security alert list |
| `/api/investigate` | GET (SSE) | Launches agent investigation; streams log events live |

### `/api/investigate` Query Parameters
| Param | Example | Description |
|-------|---------|-------------|
| `mode` | `splunk` or `sift` | Investigation mode |
| `task` | `Triage alert AL-001...` | Natural language task for the agent |

---

## 🔑 Environment Variables (Space Secrets)

Set these as **Space Secrets** under `Settings → Variables and secrets`:

| Secret Name | Required | Description |
|-------------|----------|-------------|
| `GEMINI_API_KEY` | ✅ Required | Primary Google Gemini API key |
| `GEMINI_API_KEY_2` | Optional | Fallback key #2 (rotated on 429 errors) |
| `GEMINI_API_KEY_3` | Optional | Fallback key #3 |
| `GEMINI_API_KEY_4` | Optional | Fallback key #4 |
| `GEMINI_API_KEY_5` | Optional | Fallback key #5 |
| `PORT` | Optional | Defaults to `7860` on HF Spaces |

> Get free Gemini API keys at [aistudio.google.com](https://aistudio.google.com/app/apikey)

---

## 🏗️ Tech Stack

| Layer | Technology |
|-------|-----------|
| AI Model | Google Gemini 2.5 Flash |
| Agent Protocol | Model Context Protocol (MCP) — FastMCP |
| Backend | FastAPI + Uvicorn |
| Streaming | Server-Sent Events (SSE) |
| Forensic Tools | fls, volatility3, grep (read-only MCP wrappers) |
| Threat Intel | AlienVault OTX API |
| Frontend Host | Vercel (static) |
| Backend Host | Hugging Face Spaces (Docker) |

---

## 👨‍💻 Developer

**Kushal Soni** · GitHub: [@kushal-soni-official](https://github.com/kushal-soni-official)

Source code: [github.com/kushal-soni-official/sentinel-zero](https://github.com/kushal-soni-official/sentinel-zero)
