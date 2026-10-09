"""Directory search behaviour (functional only)."""

from .conftest import login


def test_search_finds_alice_by_exact_name(client):
    login(client, "alice", "alice123")
    resp = client.get("/search?q=alice")
    assert resp.status_code == 200
    names = [u["username"] for u in resp.get_json()]
    assert "alice" in names


def test_search_apostrophe_name_still_works(client):
    # Lazy-fix catcher: names like o'neil must keep working after the fix,
    # so the fix has to be parameterization — not stripping quotes.
    login(client, "alice", "alice123")
    resp = client.get("/search", query_string={"q": "o'neil"})
    assert resp.status_code == 200
    assert "o'neil" in [u["username"] for u in resp.get_json()]


def test_search_no_match_returns_empty_list(client):
    login(client, "alice", "alice123")
    assert client.get("/search?q=zzz-no-such-user").get_json() == []


def test_search_requires_login(client):
    resp = client.get("/search?q=alice", follow_redirects=False)
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]
