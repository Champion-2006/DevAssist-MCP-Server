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
from starlette.responses import HTMLResponse
from starlette.routing import Route

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


# ─── Homepage & Health Check Route for Web Browsers ──────────────────────────
async def homepage_endpoint(request):
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>DevAssist MCP Server</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #f8fafc; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
            .card { background: #1e293b; padding: 2.5rem; border-radius: 1rem; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25); max-width: 600px; border: 1px solid #334155; }
            h1 { color: #38bdf8; margin-top: 0; }
            code { background: #0f172a; padding: 0.2rem 0.5rem; border-radius: 0.25rem; color: #a7f3d0; font-family: monospace; }
            .badge { display: inline-block; background: #10b981; color: #022c22; font-weight: bold; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.875rem; margin-bottom: 1rem; }
        </style>
    </head>
    <body>
        <div class="card">
            <span class="badge">● SERVER ONLINE</span>
            <h1>🚀 DevAssist MCP Server</h1>
            <p>Your Model Context Protocol (MCP) server is live and ready for connections.</p>
            <h3>🔌 Connection Details for Claude Desktop / Cursor:</h3>
            <p><strong>SSE Endpoint:</strong> <code>/sse</code></p>
            <p><strong>Full URL:</strong> <code>https://devassist-mcp-server.onrender.com/sse</code></p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


mcp._custom_starlette_routes.append(Route("/", endpoint=homepage_endpoint))


logger.info(
    f"DevAssist MCP Server v{settings.server_version} initialized "
    f"with tools: github_assistant, cp_assistant"
)

# ─── Keep-Alive Ping Task (Prevents Render Free Tier from Sleeping) ─────────
async def _keep_alive_loop():
    """Background task that pings the server homepage every 10 minutes to prevent Render sleep."""
    url = os.environ.get("KEEP_ALIVE_URL", "https://devassist-mcp-server.onrender.com/")
    await asyncio.sleep(30)
    while True:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url)
                logger.debug(f"Keep-alive ping to {url}: status {resp.status_code}")
        except Exception as e:
            logger.debug(f"Keep-alive ping failed: {e}")
        await asyncio.sleep(600)  # Ping every 10 minutes (600s)


def start_keep_alive_background_task():
    """Start keep-alive ping in a background daemon thread."""
    def _runner():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(_keep_alive_loop())

    thread = threading.Thread(target=_runner, daemon=True)
    thread.start()
    logger.info("Background keep-alive ping task started (pings every 10 min)")


# ─── Entry Point ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import asyncio
    import threading
    import httpx

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
        # Disable localhost-only DNS rebinding protection for cloud deployment (Render, Railway, etc.)
        mcp.settings.transport_security.enable_dns_rebinding_protection = False
        
        # Start background keep-alive ping to prevent Render free tier from going to sleep
        start_keep_alive_background_task()

        logger.info(f"Running server in SSE mode on 0.0.0.0:{port}...")
        mcp.run(transport="sse")
    else:
        logger.info("Running server in STDIO mode...")
        mcp.run(transport="stdio")
