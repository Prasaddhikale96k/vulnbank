"""Invoice viewing and receipt downloads (functional only)."""

from .conftest import login


def test_user_can_view_own_invoice(client, ids):
    login(client, "alice", "alice123")
    resp = client.get(f"/invoices/{ids['alice_invoice']}")
    assert resp.status_code == 200
    assert resp.get_json()["description"] == "Website redesign"


def test_admin_can_view_any_invoice(client, ids):
    # Lazy-fix catcher: admins legitimately open other users' invoices, so
    # the fix must be an ownership check — not "block everyone".
    login(client, "admin", "admin123")
    resp = client.get(f"/invoices/{ids['alice_invoice']}")
    assert resp.status_code == 200
    assert resp.get_json()["description"] == "Website redesign"


def test_missing_invoice_is_404(client):
    login(client, "alice", "alice123")
    assert client.get("/invoices/99999").status_code == 404


def test_invoice_requires_login(client, ids):
    resp = client.get(f"/invoices/{ids['alice_invoice']}",
                      follow_redirects=False)
    assert resp.status_code == 302


def test_download_existing_legit_file(client):
    login(client, "alice", "alice123")
    resp = client.get("/download", query_string={"file": "receipt.txt"})
    assert resp.status_code == 200
    assert b"legit receipt contents" in resp.data


def test_download_missing_file_is_404(client):
    login(client, "alice", "alice123")
    assert client.get("/download",
                      query_string={"file": "nope.txt"}).status_code == 404
