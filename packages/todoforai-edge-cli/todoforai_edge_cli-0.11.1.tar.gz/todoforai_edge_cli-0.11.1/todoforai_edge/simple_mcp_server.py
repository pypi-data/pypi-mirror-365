"""Example of how simple MCP servers could be with FastMCP"""
from fastmcp import FastMCP

# Create server
mcp = FastMCP("TodoForAI Tools")

@mcp.tool
def execute_shell(command: str) -> str:
    """Execute a shell command safely"""
    import subprocess
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        return f"Exit code: {result.returncode}\nStdout: {result.stdout}\nStderr: {result.stderr}"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool  
def read_file(path: str) -> str:
    """Read contents of a file"""
    try:
        with open(path, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

@mcp.resource("workspace://{path}")
def get_workspace_info(path: str) -> str:
    """Get workspace information"""
    import os
    if os.path.exists(path):
        return f"Workspace at {path} exists"
    return f"Workspace at {path} not found"

if __name__ == "__main__":
    # Can easily switch transports
    mcp.run(transport="sse")  # or "stdio" or "streamable-http"