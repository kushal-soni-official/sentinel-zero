import os
import sys
import json
import asyncio
import threading
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Ensure core files are in path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from core.agent import SentinelZeroAgent
from core.mcp_client import McpClient

load_dotenv()

app = FastAPI(title="Sentinel Zero Security Triage API")

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helper to push logs from worker thread to asyncio loop
class SSELoggerCallback:
    def __init__(self, loop, queue_obj):
        self.loop = loop
        self.queue = queue_obj

    def __call__(self, log_entry):
        self.loop.call_soon_threadsafe(self.queue.put_nowait, log_entry)

@app.get("/api/status")
def get_status():
    """Health check endpoint — returns server status, available modes, and registered MCP tools."""
    from core.mcp_client import McpClient
    sift_client = McpClient(mode="sift")
    splunk_client = McpClient(mode="splunk")
    return {
        "status": "online",
        "system": "Sentinel Zero",
        "version": "1.0.0",
        "model": "gemini-2.5-flash",
        "modes": {
            "splunk": {
                "description": "Splunk SIEM alert triage mode",
                "tools": [fn.__name__ for fn in splunk_client.get_gemini_tools()]
            },
            "sift": {
                "description": "SANS SIFT forensic investigation mode",
                "tools": [fn.__name__ for fn in sift_client.get_gemini_tools()]
            }
        },
        "mcp_server": "sentinel-sift-server (FastMCP)",
        "evidence_integrity": "SHA-256 verified",
        "self_correction": "enabled"
    }

@app.get("/api/alerts")
def get_alerts():
    """Returns mock Splunk security alerts for the dashboard."""
    mock_path = os.path.join("demo_data", "mock_alerts.json")
    if os.path.exists(mock_path):
        with open(mock_path, "r") as f:
            return json.load(f)
    return []

@app.get("/api/investigate")
async def investigate(mode: str = "splunk", task: str = "Investigate high-severity security incidents."):
    # Load default context based on mode
    if mode == "splunk":
        alerts_path = os.path.join("demo_data", "mock_alerts.json")
        if os.path.exists(alerts_path):
            with open(alerts_path, "r") as f:
                context = {"splunk_alerts": json.load(f)}
        else:
            context = {}
    else:
        context = {
            "forensic_image": "SEC-PROD-SRV01_disk.raw",
            "memory_dump": "SEC-PROD-SRV01_memory.dmp",
            "sift_tools": ["fls", "volatility3", "grep"]
        }

    loop = asyncio.get_running_loop()
    event_queue = asyncio.Queue()

    def run_agent_thread():
        mcp = McpClient(mode=mode)
        agent = SentinelZeroAgent(mcp_client=mcp, mode=mode)
        agent.logger.callback = SSELoggerCallback(loop, event_queue)
        
        try:
            result = agent.analyze(task, context)
            loop.call_soon_threadsafe(event_queue.put_nowait, {
                "timestamp": "",
                "type": "result",
                "data": result
            })
        except Exception as e:
            loop.call_soon_threadsafe(event_queue.put_nowait, {
                "timestamp": "",
                "type": "error",
                "message": str(e)
            })

    # Execute in a daemon thread so FastAPI doesn't block
    threading.Thread(target=run_agent_thread, daemon=True).start()

    async def event_generator():
        while True:
            item = await event_queue.get()
            yield f"data: {json.dumps(item)}\n\n"
            if item.get("type") in ["result", "error"]:
                break

    return StreamingResponse(event_generator(), media_type="text/event-stream")

from fastapi.responses import FileResponse

@app.get("/")
def get_index():
    if os.path.exists("frontend/index.html"):
        return FileResponse("frontend/index.html")
    return {"status": "Sentinel Zero API running. Frontend index.html not found."}

@app.get("/style.css")
def get_style():
    return FileResponse("frontend/style.css")

@app.get("/app.js")
def get_js():
    return FileResponse("frontend/app.js")

@app.get("/logo.png")
def get_logo():
    return FileResponse("frontend/logo.png")

@app.get("/forensics_art.png")
def get_art():
    return FileResponse("frontend/forensics_art.png")

import os
if os.path.exists("frontend/frames"):
    app.mount("/frames", StaticFiles(directory="frontend/frames"), name="frames")

if __name__ == "__main__":
    import uvicorn
    # Load configuration
    # FIX: Default port changed from 8000 → 8001 to match .env and run_dashboard.cmd
    port = int(os.getenv("PORT", 8001))
    print(f"Starting Sentinel Zero on http://localhost:{port}")
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)
