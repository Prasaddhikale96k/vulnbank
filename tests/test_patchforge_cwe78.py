from .conftest import login


def test_ping_command_injection_rejected(client):
    login(client, "admin", "admin123")
    resp = client.post("/admin/ping", json={"host": "127.0.0.1; id"})
    assert resp.status_code == 400
