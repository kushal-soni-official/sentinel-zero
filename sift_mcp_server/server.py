import sys
import os

# Append current directory to path so imports work correctly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from mcp.server.fastmcp import FastMCP
import sift_mcp_server.tools as tools

mcp = FastMCP("sentinel-sift-server")

@mcp.tool()
def get_filesystem_timeline(image_path: str) -> dict:
    """Extract file system timeline. Safe read-only tool. Use 'mock' to load demo data."""
    return tools.get_filesystem_timeline(image_path)

@mcp.tool()
def analyze_memory_dump(image_path: str) -> dict:
    """Parse memory dumps for malware (e.g. process list). Safe read-only. Use 'mock' to load demo data."""
    return tools.analyze_memory_dump(image_path)

@mcp.tool()
def search_indicators_of_compromise(ioc_pattern: str, search_path: str = "demo_data") -> dict:
    """Search files/logs in search_path for a keyword or IOC signature (grep). Safe read-only."""
    return tools.search_indicators_of_compromise(ioc_pattern, search_path)

@mcp.tool()
def verify_evidence_hash(target_path: str = "mock") -> dict:
    """Compute SHA-256 hash of a forensic target to verify evidence integrity before and after analysis. Use 'mock' for demo data."""
    return tools.verify_evidence_hash(target_path)

@mcp.tool()
def query_live_threat_intel(indicator: str) -> dict:
    """Query live public Threat Intelligence APIs for IPs and Hashes."""
    return tools.query_live_threat_intel(indicator)

if __name__ == "__main__":
    mcp.run()
