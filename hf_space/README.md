---
title: Sentinel Zero
emoji: 🛡️
colorFrom: blue
colorTo: cyan
sdk: docker
pinned: true
---

# Sentinel Zero — Backend API

FastAPI backend powering the **Sentinel Zero** autonomous AI security triage agent.

- **Model:** Google Gemini 2.5 Flash
- **Protocol:** MCP (Model Context Protocol)
- **Streaming:** Server-Sent Events (SSE)
- **Live Intel:** AlienVault OTX API

## Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/status` | GET | System health check |
| `/api/alerts` | GET | Fetch Splunk security alerts |
| `/api/investigate` | GET | Start SSE agent investigation stream |

## Environment Variables / Secrets

Set `GEMINI_API_KEY` as a **Space Secret** (not in code):
> Settings → Variables and secrets → New secret → `GEMINI_API_KEY`

## Frontend

Live UI: [https://sentinel-zero.vercel.app](https://sentinel-zero.vercel.app)
