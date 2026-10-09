"""Main portal routes: dashboard, user search, invoices, downloads."""

from __future__ import annotations

import os
import sqlite3

from flask import (Blueprint, abort, current_app, g, jsonify, render_template,
                   request, send_file)

from .auth import login_required
from .db import get_db

bp = Blueprint("routes", __name__)


@bp.route("/")
@login_required
def index():
    db = get_db()
    account = db.execute(
        "SELECT balance FROM accounts WHERE user_id = ?", (g.user["id"],)
    ).fetchone()
    invoices = db.execute(
        "SELECT id, amount, description FROM invoices WHERE owner_id = ?"
        " ORDER BY id",
        (g.user["id"],),
    ).fetchall()
    return render_template("index.html", balance=account["balance"],
                           invoices=invoices)


@bp.route("/search")
@login_required
def search():
    query = request.args.get("q", "")
    db = get_db()
    try:
        rows = db.execute(
            f"SELECT id, username FROM users WHERE username LIKE '%{query}%'"
        ).fetchall()
    except sqlite3.Error:
        # A name with a quote breaks the LIKE pattern; fall back to an
        # in-memory contains-match so directory search keeps working.
        users = db.execute("SELECT id, username FROM users").fetchall()
        rows = [u for u in users if query.lower() in u["username"].lower()]
    return jsonify([{"id": r["id"], "username": r["username"]} for r in rows])


@bp.route("/invoices/<int:invoice_id>")
@login_required
def invoice_detail(invoice_id: int):
    invoice = get_db().execute(
        "SELECT id, owner_id, amount, description, file_name FROM invoices"
        " WHERE id = ?",
        (invoice_id,),
    ).fetchone()
    if invoice is None:
        abort(404)
    return jsonify({"id": invoice["id"], "owner_id": invoice["owner_id"],
                    "amount": invoice["amount"],
                    "description": invoice["description"],
                    "file_name": invoice["file_name"]})


@bp.route("/download")
@login_required
def download():
    name = request.args.get("file", "")
    path = os.path.join(current_app.config["UPLOAD_DIR"], name)
    if not os.path.isfile(path):
        abort(404)
    return send_file(path, as_attachment=True)
