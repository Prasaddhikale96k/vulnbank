"""Admin utilities (functional only; subprocess is mocked)."""

from unittest import mock

from .conftest import login


def test_admin_user_list(client):
    login(client, "admin", "admin123")
    resp = client.get("/admin/users")
    assert resp.status_code == 200
    names = [u["username"] for u in resp.get_json()]
    assert {"alice", "bob", "admin"} <= set(names)


def test_user_list_forbidden_for_non_admin(client):
    login(client, "alice", "alice123")
    assert client.get("/admin/users").status_code == 403


def test_ping_valid_host_returns_200(client):
    login(client, "admin", "admin123")
    completed = mock.Mock(returncode=0, stdout="PING ok")
    with mock.patch("app.admin.subprocess.run",
                    return_value=completed) as run:
        resp = client.post("/admin/ping", json={"host": "127.0.0.1"})
    assert resp.status_code == 200
    assert resp.get_json()["returncode"] == 0
    run.assert_called_once()


def test_ping_missing_host_is_400(client):
    login(client, "admin", "admin123")
    assert client.post("/admin/ping", json={}).status_code == 400


def test_ping_forbidden_for_non_admin(client):
    login(client, "bob", "bob123")
    assert client.post("/admin/ping",
                       json={"host": "127.0.0.1"}).status_code == 403


def test_ping_requires_login(client):
    resp = client.post("/admin/ping", json={"host": "127.0.0.1"},
                       follow_redirects=False)
    assert resp.status_code == 302
