import json
import os
import sift_mcp_server.tools as sift_tools

class McpClient:
    def __init__(self, mode="sift"):
        self.mode = mode

    def get_gemini_tools(self):
        """
        Returns a list of Python functions that Gemini can use as tools.
        Gemini's google.generativeai SDK supports passing a list of Python functions directly!
        """
        if self.mode == "sift":
            return [
                self.get_filesystem_timeline,
                self.analyze_memory_dump,
                self.search_indicators_of_compromise,
                self.verify_evidence_hash,
                self.query_live_threat_intel
            ]
        elif self.mode == "splunk":
            return [
                self.get_splunk_alerts,
                self.acknowledge_splunk_alert,
                self.search_indicators_of_compromise,
                self.query_live_threat_intel
            ]
        return []

    # SIFT Tools
    def get_filesystem_timeline(self, image_path: str = "mock") -> str:
        """
        Extract the file system timeline/listing using the SIFT fls tool. 
        Provides inode, size, timestamps, and path names. Safe read-only tool.
        Use 'mock' to load demo data.
        """
        result = sift_tools.get_filesystem_timeline(image_path)
        return json.dumps(result)

    def analyze_memory_dump(self, image_path: str = "mock") -> str:
        """
        Analyze a RAM memory dump using Volatility to list processes (windows.pslist). 
        Safe read-only tool. Use 'mock' to load demo data.
        """
        result = sift_tools.analyze_memory_dump(image_path)
        return json.dumps(result)

    def verify_evidence_hash(self, target_path: str = "mock") -> str:
        """
        Compute SHA-256 hash of a forensic evidence target to prove integrity.
        Run before and after analysis to confirm the agent did not alter any case data.
        Use 'mock' to hash all demo_data files.
        """
        result = sift_tools.verify_evidence_hash(target_path)
        return json.dumps(result)

    def query_live_threat_intel(self, indicator: str) -> str:
        """
        Query live public Threat Intelligence APIs for IPs and Hashes.
        Provides real-world validation to avoid hallucination.
        """
        result = sift_tools.query_live_threat_intel(indicator)
        return json.dumps(result)

    # Splunk Tools
    def get_splunk_alerts(self) -> str:
        """
        Fetch security alerts from the Splunk Enterprise instance. 
        Returns security alert history with details like process, user, and command lines.
        """
        mock_path = os.path.join("demo_data", "mock_alerts.json")
        if os.path.exists(mock_path):
            with open(mock_path, "r") as f:
                content = f.read()
            return content
        return json.dumps({"error": "No Splunk alerts found"})

    def acknowledge_splunk_alert(self, alert_id: str) -> str:
        """
        Acknowledge a Splunk alert to mark it as triaged/in-progress.
        """
        return json.dumps({"status": "success", "alert_id": alert_id, "message": "Alert marked as triaged by Sentinel Zero"})

    # Shared Tools
    def search_indicators_of_compromise(self, ioc_pattern: str, search_path: str = "demo_data") -> str:
        """
        Search files, logs, or directories for a keyword or Indicator of Compromise (IOC) signature.
        Acts as a safe read-only search tool.
        """
        result = sift_tools.search_indicators_of_compromise(ioc_pattern, search_path)
        return json.dumps(result)

    def _ensure_json_string(self, value):
        """Ensure value is a JSON string — normalizes tool return types."""
        if isinstance(value, str):
            return value
        try:
            return json.dumps(value)
        except (TypeError, ValueError):
            return json.dumps({"raw": str(value)})

    def call_tool(self, tool_name, arguments):
        """
        Call a tool by name with arguments (acts as a local dispatcher).
        Always returns a JSON string for consistent parsing in agent.py.
        """
        tool_func = getattr(self, tool_name, None)
        if tool_func:
            try:
                result = tool_func(**arguments)
                return self._ensure_json_string(result)
            except TypeError as e:
                # Handle unexpected keyword arguments gracefully
                return json.dumps({"error": f"Argument error calling {tool_name}: {str(e)}"})
            except Exception as e:
                return json.dumps({"error": f"Error calling {tool_name}: {str(e)}"})
        return json.dumps({"error": f"Tool '{tool_name}' not found in mode '{self.mode}'"})
