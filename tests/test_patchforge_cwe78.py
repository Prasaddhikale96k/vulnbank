"""Regression tests for CWE-78 command-injection in /admin/ping."""

from unittest import mock

from .conftest import login


def test_ping_command_injection_rejected(client):
    """Attacker-supplied shell metacharacters must be rejected, not executed."""
    login(client, "admin", "admin123")
    attack_hosts = [
        "127.0.0.1;id",
        "127.0.0.1 && rm -rf /",
        "127.0.0.1 | cat /etc/passwd",
        "$(cat /etc/passwd)",
        "`id`",
        "127.0.0.1\ncat /etc/passwd",
        "127.0.0.1 -O -V",
        "-h",
    ]
    for host in attack_hosts:
        with mock.patch("app.admin.subprocess.run") as run:
            resp = client.post("/admin/ping", json={"host": host})
        assert resp.status_code == 400, (
            f"host {host!r} should be rejected with 400, got {resp.status_code}")
        body = resp.get_json(silent=True) or {}
        assert body.get("error") == "invalid host", (
            f"host {host!r} should return invalid-host error, got {body}")
        run.assert_not_called()


def test_ping_valid_hosts_still_accepted(client):
    """Valid hostnames and IPv4s must continue to return 200 (existing behaviour)."""
    login(client, "admin", "admin123")
    for host in ("127.0.0.1", "localhost", "example.com", "my-server-01.internal"):
        with mock.patch("app.admin.subprocess.run",
                        return_value=mock.Mock(returncode=0, stdout="PING ok")) as run:
            resp = client.post("/admin/ping", json={"host": host})
        assert resp.status_code == 200, (
            f"valid host {host!r} should return 200, got {resp.status_code}")
        assert resp.get_json()["returncode"] == 0
        run.assert_called_once()


def test_ping_uses_list_not_shell_command(client):
    """Confirm the subprocess call uses an argument list, never a string+shell."""
    login(client, "admin", "admin123")
    with mock.patch("app.admin.subprocess.run",
                    return_value=mock.Mock(returncode=0, stdout="PING ok")) as run:
        resp = client.post("/admin/ping", json={"host": "127.0.0.1"})
    assert resp.status_code == 200
    run.assert_called_once()
    args, kwargs = run.call_args
    # First arg must be a list (not a shell string) ...
    assert isinstance(args[0], (list, tuple)), \
        f"expected argument list, got {type(args[0])}: {args[0]!r}"
    assert args[0] == ["ping", "-c", "1", "127.0.0.1"]
    # ... and shell=True must never be passed.
    assert kwargs.get("shell") is not True, "subprocess.run must not use shell=True"
