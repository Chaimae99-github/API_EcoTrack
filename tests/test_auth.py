# tests/test_auth.py

def test_register_and_login(client):
    # Register
    resp = client.post(
        "/auth/register",
        json={
            "email": "testuser@example.com",
            "password": "password123",
            "role": "user",
            "is_active": True,
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "testuser@example.com"
    assert data["role"] == "user"

    # Login
    resp = client.post(
        "/auth/login",
        data={
            "username": "testuser@example.com",
            "password": "password123",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp.status_code == 200
    token_data = resp.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
