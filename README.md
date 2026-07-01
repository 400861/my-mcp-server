# my-mcp-server — 3-layer HTTP + MCP demo

A small, all-Python demo of three layers wired together over HTTP:

```
VS Code (native MCP client)
        │  HTTP  →  http://127.0.0.1:9100/mcp
        ▼
MCP server  (mcp_server/server.py, Streamable HTTP transport)
        │  HTTP  →  http://127.0.0.1:8000
        ▼
HTTP API server  (http_server/app.py, Flask, GET endpoints)
        │
        ▼
   in-memory "books" data
```

- **Layer 1 — HTTP API** ([http_server/app.py](http_server/app.py)): a plain Flask
  REST-ish API with GET endpoints. Knows nothing about MCP.
- **Layer 2 — MCP server** ([mcp_server/server.py](mcp_server/server.py)): exposes MCP
  *tools* over the Streamable HTTP transport. Each tool calls a layer-1 endpoint
  with `httpx`.
- **Layer 3 — VS Code**: uses its built-in MCP client via
  [.vscode/mcp.json](.vscode/mcp.json) to connect to layer 2 over HTTP. No custom
  extension or Node.js needed.

## Setup

```powershell
python -m pip install -r requirements.txt
```

## Run (two terminals)

Terminal 1 — the HTTP API (port 8000):

```powershell
python http_server/app.py
```

Terminal 2 — the MCP server (port 9100):

```powershell
python mcp_server/server.py
```

> Port 9100 is used because 9000 is occupied by Zscaler (ZSATunnel) on this
> machine. Override any port with env vars: `HTTP_SERVER_PORT`,
> `MCP_SERVER_PORT`, `HTTP_API_BASE_URL`.

## Verify the chain

With both servers running:

```powershell
python mcp_server/test_client.py
```

Expected: it lists the tools (`list_books`, `get_book`, `list_genres`,
`api_health`) and prints results proxied from the Flask API.

## Use from VS Code

1. Open this folder in VS Code (MCP support requires a recent VS Code build).
2. With both servers running, VS Code reads [.vscode/mcp.json](.vscode/mcp.json)
   and connects to `http://127.0.0.1:9100/mcp`.
3. Start the server from the `mcp.json` gutter "Start" action (or the
   **MCP: List Servers** command), then use the tools from Copilot Chat's
   Agent mode.

## HTTP API endpoints (layer 1)

| Method | Path                  | Description                                   |
| ------ | --------------------- | --------------------------------------------- |
| GET    | `/health`             | Liveness probe                                |
| GET    | `/books`              | List books; filters: `?genre=`, `?author=`    |
| GET    | `/books/<id>`         | Single book by id                             |
| GET    | `/genres`             | Distinct genres                               |

## MCP tools (layer 2)

| Tool          | Calls                 |
| ------------- | --------------------- |
| `list_books`  | `GET /books`          |
| `get_book`    | `GET /books/<id>`     |
| `list_genres` | `GET /genres`         |
| `api_health`  | `GET /health`         |
