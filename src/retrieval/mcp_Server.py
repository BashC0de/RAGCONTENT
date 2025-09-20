"""
mcp_server.py
-------------
Official MCP server exposing the RAG retrieval tool.
"""
# from mcp.fastapi import MCPApp, tool
from fastapi import FastAPI, tool, MCPApp

# from modelcontextprotocol.fastapi import MCPApp, tool
from src.retrieval.retriever import retrieve_for_query
from src.utils.logger import logger

# Create an MCP application (FastAPI-compatible)
app = MCPApp()

@tool()   # registers as an MCP tool
async def retrieve_context(query: str, top_k: int = 8) -> dict:
    """
    Retrieve top-k documents relevant to the query.
    This method is automatically discoverable by any MCP client.
    """
    logger.info(f"[MCP] retrieve_context query={query}, top_k={top_k}")
    docs = retrieve_for_query(query, top_k=top_k)
    return {"documents": docs}
