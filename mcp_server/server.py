"""Layer 2: An MCP server that fronts the HTTP API (layer 1).

It exposes MCP *tools* to clients. Each tool makes an HTTP GET call to the
Flask API and returns the result. The MCP server itself is served over the
Streamable HTTP transport, so clients (layer 3, e.g. VS Code) connect to it
over HTTP at:  http://127.0.0.1:9100/mcp

Run:
    python mcp_server/server.py

Env vars:
    HTTP_API_BASE_URL   base url of the Flask API   (default http://127.0.0.1:8000)
    MCP_SERVER_HOST     host to bind                 (default 127.0.0.1)
    MCP_SERVER_PORT     port to bind                 (default 9100)
"""

import os

import httpx
from mcp.server.fastmcp import FastMCP

HTTP_API_BASE_URL = os.environ.get("HTTP_API_BASE_URL", "http://127.0.0.1:8000")
MCP_SERVER_HOST = os.environ.get("MCP_SERVER_HOST", "127.0.0.1")
MCP_SERVER_PORT = int(os.environ.get("MCP_SERVER_PORT", "9100"))

# host/port are read by the streamable-http transport when we call .run().
mcp = FastMCP("books-mcp", host=MCP_SERVER_HOST, port=MCP_SERVER_PORT)


def _get(path: str, params: dict | None = None) -> dict:
    """Helper: GET a path on the backing HTTP API and return parsed JSON."""
    url = f"{HTTP_API_BASE_URL}{path}"
    with httpx.Client(timeout=10.0) as client:
        resp = client.get(url, params=params)
        resp.raise_for_status()
        return resp.json()


@mcp.tool()
def list_books(genre: str | None = None, author: str | None = None) -> dict:
    """List books from the catalog.

    Args:
        genre: optional exact genre filter (e.g. "software", "sci-fi", "history").
        author: optional case-insensitive substring match on the author name.
    """
    params = {}
    if genre:
        params["genre"] = genre
    if author:
        params["author"] = author
    return _get("/books", params=params)


@mcp.tool()
def get_book(book_id: int) -> dict:
    """Get details for a single book by its numeric id."""
    return _get(f"/books/{book_id}")


@mcp.tool()
def list_genres() -> dict:
    """List the distinct genres available in the catalog."""
    return _get("/genres")


@mcp.tool()
def api_health() -> dict:
    """Check that the backing HTTP API is reachable and healthy."""
    return _get("/health")


if __name__ == "__main__":
    # Serve MCP over Streamable HTTP. The endpoint is mounted at /mcp.
    mcp.run(transport="streamable-http")
