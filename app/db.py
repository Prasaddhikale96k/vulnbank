"""SQLite helpers and seed data for VulnBank."""

from __future__ import annotations

import sqlite3

import click
from flask import current_app, g
from werkzeug.security import generate_password_hash


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(exc: BaseException | None = None) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'user'
);
CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id),
    balance REAL NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    owner_id INTEGER NOT NULL REFERENCES users(id),
    amount REAL NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    file_name TEXT NOT NULL DEFAULT ''
);
"""


def init_db() -> None:
    db = get_db()
    db.executescript(_SCHEMA)
    if db.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
        seed()


def seed() -> None:
    db = get_db()
    users = [
        ("alice", "alice123", "user"),
        ("bob", "bob123", "user"),
        ("o'neil", "oneil123", "user"),
        ("admin", "admin123", "admin"),
    ]
    ids: dict[str, int] = {}
    for username, password, role in users:
        cur = db.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username, generate_password_hash(password), role),
        )
        ids[username] = cur.lastrowid
        db.execute("INSERT INTO accounts (user_id, balance) VALUES (?, ?)",
                   (cur.lastrowid, 1000.0))
    invoices = [
        (ids["alice"], 250.0, "Website redesign", "invoice_1.pdf"),
        (ids["alice"], 99.5, "Logo tweaks", "invoice_2.pdf"),
        (ids["bob"], 420.0, "Consulting, March", "invoice_1.pdf"),
        (ids["admin"], 1.0, "Internal adjustment", "invoice_2.pdf"),
    ]
    for owner_id, amount, description, file_name in invoices:
        db.execute(
            "INSERT INTO invoices (owner_id, amount, description, file_name)"
            " VALUES (?, ?, ?, ?)",
            (owner_id, amount, description, file_name),
        )
    db.commit()


@click.command("init-db")
def init_db_command() -> None:
    init_db()
    click.echo("Database initialised.")
