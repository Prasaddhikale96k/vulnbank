"""Login, logout and dashboard behaviour."""

from .conftest import login


def test_login_valid_alice(client):
    resp = login(client, "alice", "alice123")
    assert resp.status_code == 302
    home = client.get("/", follow_redirects=False)
    assert home.status_code == 200
    assert b"alice" in home.data


def test_login_invalid_password(client):
    resp = login(client, "alice", "wrongpassword")
    assert resp.status_code == 200
    assert b"Invalid username or password" in resp.data


def test_login_unknown_user(client):
    resp = login(client, "Mallory", "whatever")
    assert b"Invalid username or password" in resp.data


def test_logout_clears_session(client):
    login(client, "alice", "alice123")
    assert client.get("/").status_code == 200
    client.get("/logout")
    assert client.get("/").status_code == 302


def test_dashboard_shows_balance_and_invoices(client):
    login(client, "alice", "alice123")
    resp = client.get("/")
    assert b"1000.0" in resp.data
    assert b"Website redesign" in resp.data


def test_anonymous_dashboard_redirects_to_login(client):
    resp = client.get("/", follow_redirects=False)
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]
