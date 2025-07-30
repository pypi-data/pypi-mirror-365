"""
Main server module for Kontext MCP server.
"""

from mcp.server.fastmcp import FastMCP
from kontext_mcp.config import KontextConfig
from kontext_mcp.register import register_tools
from kontext_mcp.logging_util import get_logger

logger = get_logger(__name__)


def main():
    """Main entry point for the Kontext MCP server."""
    logger.info("Starting Kontext MCP server...")

    # Create FastMCP instance
    mcp = FastMCP(
        "Kontext MCP Server",
        instructions="""
    This server provides tools for remembering and recalling facts.
    Use the 'remember' tool to store facts, context, or thoughts.
    Use the 'recall' tool to retrieve relevant memories based on a query.
    """,
    )

    # Register tools
    register_tools(mcp)

    logger.info("Kontext MCP server ready")

    # Run the server
    mcp.run()


if __name__ == "__main__":
    main()
