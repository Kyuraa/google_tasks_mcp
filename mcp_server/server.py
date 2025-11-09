import sys
import os
from fastmcp import FastMCP

# Add the parent directory to sys.path so we can import fastapi_backend
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from fastapi_backend.main import app as server_app

# Create an MCP server from your FastAPI app
mcp = FastMCP.from_fastapi(app=server_app)

if __name__ == "__main__":
    mcp.run()
