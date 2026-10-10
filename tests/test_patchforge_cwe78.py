from unittest import mock
from .conftest import login

def test_ping_command_injection_rejected(client):
    login(client, "admin", "admin123")
    with mock.patch("app.admin.subprocess.run") as run:
        # Payloads that attempt shell injection or flag injection should be rejected
        for payload in ["127.0.0.1; id", "localhost | ls", "-u root 127.0.0.1", " "]:
            resp = client.post("/admin/ping", json={"host": payload})
            assert resp.status_code == 400
            assert resp.get_json()["error"] == "invalid host"
        run.assert_not_called()

def test_ping_valid_ips_still_work(client):
    login(client, "admin", "admin123")
    completed = mock.Mock(returncode=0, stdout="PING 127.0.0.1 (127.0.0.1) 56(84) bytes of data.")
    with mock.patch("app.admin.subprocess.run", return_value=completed) as run:
        for host in ["127.0.0.1", "localhost", "my-server.internal"]:
            resp = client.post("/admin/ping", json={"host": host})
            assert resp.status_code == 200
            assert resp.get_json()["host"] == host
        
        # Verify the last call was secure (list of arguments, shell=False)
        run.assert_called_with(
            ["ping", "-c", "1", "my-server.internal"],
            shell=False,
            capture_output=True,
            text=True,
            timeout=15
        )
