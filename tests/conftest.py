"""Shared fixtures: temp-DB app, test client and login helper."""

from __future__ import annotations

import pytest

from app import create_app
from app.db import init_db


@pytest.fixture()
def app(tmp_path):
    db_path = tmp_path / "test.sqlite"
    uploads = tmp_path / "uploads"
    uploads.mkdir()
    (uploads / "receipt.txt").write_text("legit receipt contents\n")
    application = create_app({
        "TESTING": True,
        "DATABASE": str(db_path),
        "UPLOAD_DIR": str(uploads),
    })
    with application.app_context():
        init_db()
    yield application


@pytest.fixture()
def client(app):
    return app.test_client()


def login(client, username, password):
    return client.post("/login",
                       data={"username": username, "password": password},
                       follow_redirects=False)


@pytest.fixture()
def ids(app):
    """Primary keys of the seeded rows."""
    import sqlite3
    db = sqlite3.connect(app.config["DATABASE"])
    try:
        alice_invoice = db.execute(
            "SELECT id FROM invoices WHERE owner_id = "
            "(SELECT id FROM users WHERE username='alice') ORDER BY id"
        ).fetchone()[0]
        bob_invoice = db.execute(
            "SELECT id FROM invoices WHERE owner_id = "
            "(SELECT id FROM users WHERE username='bob') ORDER BY id"
        ).fetchone()[0]
    finally:
        db.close()
    return {"alice_invoice": alice_invoice, "bob_invoice": bob_invoice}
