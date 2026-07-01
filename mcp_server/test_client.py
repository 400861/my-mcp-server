"""Quick end-to-end check: connect to the MCP server over HTTP,
list tools, and call a couple. Mirrors what VS Code does natively.

Run (with both servers up):
    python mcp_server/test_client.py
"""

import asyncio
import os

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

MCP_URL = os.environ.get("MCP_URL", "http://127.0.0.1:9100/mcp")


async def main() -> None:
    async with streamablehttp_client(MCP_URL) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("Tools:", [t.name for t in tools.tools])

            health = await session.call_tool("api_health", {})
            print("api_health ->", health.content[0].text)

            books = await session.call_tool("list_books", {"genre": "software"})
            print("list_books(software) ->", books.content[0].text)


if __name__ == "__main__":
    asyncio.run(main())
