"""Layer 1: A plain HTTP API server (Flask).

Exposes a few GET endpoints backed by an in-memory "books" dataset.
This server knows nothing about MCP -- it's just a normal REST-ish API.
The MCP server (layer 2) calls these endpoints over HTTP.

Run:
    python http_server/app.py
Defaults to http://127.0.0.1:8000
"""

import os

from flask import Flask, jsonify, request

app = Flask(__name__)

# --- In-memory sample data -------------------------------------------------

BOOKS = [
    {"id": 1, "title": "The Pragmatic Programmer", "author": "Hunt & Thomas", "year": 1999, "genre": "software"},
    {"id": 2, "title": "Clean Code", "author": "Robert C. Martin", "year": 2008, "genre": "software"},
    {"id": 3, "title": "The Mythical Man-Month", "author": "Fred Brooks", "year": 1975, "genre": "software"},
    {"id": 4, "title": "Dune", "author": "Frank Herbert", "year": 1965, "genre": "sci-fi"},
    {"id": 5, "title": "Neuromancer", "author": "William Gibson", "year": 1984, "genre": "sci-fi"},
    {"id": 6, "title": "Sapiens", "author": "Yuval Noah Harari", "year": 2011, "genre": "history"},
]


# --- Endpoints -------------------------------------------------------------

@app.get("/health")
def health():
    """Liveness probe."""
    return jsonify({"status": "ok"})


@app.get("/books")
def list_books():
    """List books, optionally filtered by ?genre= and/or ?author= (substring)."""
    genre = request.args.get("genre")
    author = request.args.get("author")

    results = BOOKS
    if genre:
        results = [b for b in results if b["genre"].lower() == genre.lower()]
    if author:
        results = [b for b in results if author.lower() in b["author"].lower()]

    return jsonify({"count": len(results), "books": results})


@app.get("/books/<int:book_id>")
def get_book(book_id: int):
    """Fetch a single book by id."""
    for book in BOOKS:
        if book["id"] == book_id:
            return jsonify(book)
    return jsonify({"error": f"book {book_id} not found"}), 404


@app.get("/genres")
def list_genres():
    """List the distinct genres available."""
    genres = sorted({b["genre"] for b in BOOKS})
    return jsonify({"genres": genres})


if __name__ == "__main__":
    port = int(os.environ.get("HTTP_SERVER_PORT", "8000"))
    app.run(host="127.0.0.1", port=port, debug=False)
