"""Test for SQL injection vulnerability in /search endpoint (CWE-89)."""

import pytest

from .conftest import login


def test_search_sql_injection_prevented(client):
    """
    Test that SQL injection attempts in the search parameter are prevented.
    
    With the vulnerable f-string interpolation, a payload like 
    "' OR 1=1 --" would match all users. With the parameterized query
    fix, this should be treated as a literal string and only match
    users whose username actually contains that pattern (none should).
    """
    login(client, "alice", "alice123")
    
    # Attempt SQL injection using OR 1=1 to try to match all users
    resp = client.get("/search?q=' OR '1'='1")
    
    # Should return 200 (search endpoint works) but with no results
    # because no username contains the literal string ' OR '1'='1
    assert resp.status_code == 200
    results = resp.get_json()
    
    # If SQL injection worked, we'd see all users (alice, bob, admin)
    # The parameterized query should return no results for this payload
    usernames = [user["username"] for user in results]
    assert "alice" not in usernames
    assert "bob" not in usernames
    assert "admin" not in usernames


def test_search_sql_injection_union_attacks(client):
    """
    Test that UNION-based SQL injection is prevented.
    
    A UNION attack attempts to extract data from other tables.
    With parameterized queries, this should safely return no results
    or limited results, not arbitrary data.
    """
    login(client, "bob", "bob123")
    
    # UNION-based injection attempt
    resp = client.get("/search?q=' UNION SELECT id, password FROM users --")
    
    assert resp.status_code == 200
    results = resp.get_json()
    
    # Should not leak any user data
    for user in results:
        # Verify no passwords are exposed
        assert "password" not in user
        # The username should not be a valid username from the database
        # unless it literally matches the injected string
        if user.get("username"):
            # Check if this is a real user that actually contains our pattern
            # In this case, no user should match the UNION payload literally
            assert user["username"].lower() != "alice"
            assert user["username"].lower() != "bob"
            assert user["username"].lower() != "admin"


def test_search_legitimate_query_still_works(client):
    """
    Test that legitimate search queries still work after the fix.
    """
    login(client, "alice", "alice123")
    
    # Search for 'ali' - should find alice
    resp = client.get("/search?q=ali")
    assert resp.status_code == 200
    results = resp.get_json()
    usernames = [user["username"] for user in results]
    assert "alice" in usernames


def test_search_with_quote_in_input(client):
    """
    Test that quotes in input are handled safely.
    
    Previously, quotes could break the SQL query or enable injection.
    With parameterized queries, quotes are treated as literal characters.
    """
    login(client, "bob", "bob123")
    
    # Search with a quote - should not cause an error and should return
    # no results (no username contains a literal quote)
    resp = client.get("/search?q=o'brien")
    
    assert resp.status_code == 200
    results = resp.get_json()
    # Should be an empty list or only users with literal quotes in names
    # (which none of our seed users have)
    for user in results:
        assert user["username"].lower() != "alice"
        assert user["username"].lower() != "bob"
        assert user["username"].lower() != "admin"
