"""
DevAssist MCP Server — Entry Point.

A production-ready Model Context Protocol (MCP) server that exposes
GitHub and Codeforces tools for AI assistants like Claude Desktop,
Cursor, and VS Code Copilot.
"""

import os
import sys

# Ensure working directory and python path point to project root
project_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(project_dir)
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

from mcp.server.fastmcp import FastMCP

from config import settings
from tools.cp import register_cp_tools
from tools.github import register_github_tools
from utils.logger import get_logger

logger = get_logger(__name__)

# ─── Create MCP Server ───────────────────────────────────────────────────────
mcp = FastMCP(
    name=settings.server_name,
)

# ─── Register Tools ──────────────────────────────────────────────────────────
register_github_tools(mcp)
register_cp_tools(mcp)

logger.info(
    f"DevAssist MCP Server v{settings.server_version} initialized "
    f"with tools: github_assistant, cp_assistant"
)

# ─── Entry Point ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    logger.info("Starting DevAssist MCP Server...")
    logger.info(
        f"GitHub token: {'configured' if settings.github_token else 'not set'}"
    )

    # Allow setting transport via CLI flag --sse or environment variable TRANSPORT=sse
    transport_mode = os.environ.get("TRANSPORT", settings.transport).lower()
    if "--sse" in sys.argv or transport_mode == "sse":
        port = int(os.environ.get("PORT", settings.port))
        mcp.settings.host = "0.0.0.0"
        mcp.settings.port = port
        logger.info(f"Running server in SSE mode on 0.0.0.0:{port}...")
        mcp.run(transport="sse")
    else:
        logger.info("Running server in STDIO mode...")
        mcp.run(transport="stdio")
