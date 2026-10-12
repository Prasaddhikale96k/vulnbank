from unittest import mock
from .conftest import login

def test_ping_command_injection_mitigated(client):
    login(client, "admin", "admin123")
    with mock.patch("app.admin.subprocess.run") as run:
        # Command injection attempt should be rejected by validation
        resp = client.post("/admin/ping", json={"host": "127.0.0.1; ls"})
        assert resp.status_code == 400
        run.assert_not_called()

def test_ping_ipv6_supported(client):
    login(client, "admin", "admin123")
    completed = mock.Mock(returncode=0, stdout="PING ::1 ok")
    with mock.patch("app.admin.subprocess.run", return_value=completed) as run:
        # Valid IPv6 address should be allowed and passed correctly as an argument
        resp = client.post("/admin/ping", json={"host": "::1"})
        assert resp.status_code == 200
        run.assert_called_once_with(
            ["ping", "-c", "1", "::1"],
            capture_output=True, text=True, timeout=15
        )

def test_ping_argument_injection_mitigated(client):
    login(client, "admin", "admin123")
    with mock.patch("app.admin.subprocess.run") as run:
        # Host starting with hyphen should be rejected to prevent argument injection
        resp = client.post("/admin/ping", json={"host": "-c"})
        assert resp.status_code == 400
        run.assert_not_called()

def test_ping_ipv4_valid(client):
    login(client, "admin", "admin123")
    completed = mock.Mock(returncode=0, stdout="PING 127.0.0.1 ok")
    with mock.patch("app.admin.subprocess.run", return_value=completed) as run:
        # Valid IPv4 address should be allowed
        resp = client.post("/admin/ping", json={"host": "127.0.0.1"})
        assert resp.status_code == 200
        run.assert_called_once()
