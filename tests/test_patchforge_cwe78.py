from __future__ import annotations

from unittest import mock
from .conftest import login


def test_ping_command_injection_rejected(client):
    login(client, "admin", "admin123")
    resp = client.post("/admin/ping", json={"host": "127.0.0.1; touch /tmp/pwned"})
    assert resp.status_code == 400


def test_ping_ipv6_accepted(client):
    login(client, "admin", "admin123")
    completed = mock.Mock(returncode=0, stdout="PING ipv6 ok")
    with mock.patch("app.admin.subprocess.run", return_value=completed) as run:
        resp = client.post("/admin/ping", json={"host": "2001:db8::1"})
    assert resp.status_code == 200
    assert resp.get_json()["returncode"] == 0
    run.assert_called_once()
