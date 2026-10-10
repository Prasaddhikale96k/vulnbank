"""Admin utilities: user list and connectivity checks."""

from __future__ import annotations

import re
import subprocess  # nosec B404 - admin-only network diagnostic

from flask import Blueprint, g, jsonify, request

from .auth import admin_required
from .db import get_db

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.route("/users")
@admin_required
def user_list():
    rows = get_db().execute(
        "SELECT id, username, role FROM users ORDER BY id").fetchall()
    return jsonify([{"id": r["id"], "username": r["username"],
                     "role": r["role"]} for r in rows])


@bp.route("/ping", methods=["POST"])
@admin_required
def ping():
    host = (request.get_json(silent=True) or {}).get("host", "")
    if not host:
        return jsonify({"error": "host is required"}), 400
    if not re.fullmatch(r"[A-Za-z0-9.-]{1,253}", host) or host.startswith("-"):
        return jsonify({"error": "invalid host"}), 400
    completed = subprocess.run(["ping", "-c", "1", host], shell=False,
                               capture_output=True, text=True, timeout=15)
    return jsonify({"host": host, "returncode": completed.returncode,
                    "output": completed.stdout[-500:],
                    "admin": g.user["username"]})
