def test_health_check(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert data["status"] == "healthy"


def test_register(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"username": "newuser", "password": "Test1234", "confirm_password": "Test1234"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["username"] == "newuser"


def test_register_duplicate_username(client):
    client.post(
        "/api/v1/auth/register",
        json={"username": "dupuser", "password": "Test1234", "confirm_password": "Test1234"},
    )
    response = client.post(
        "/api/v1/auth/register",
        json={"username": "dupuser", "password": "Test1234", "confirm_password": "Test1234"},
    )
    assert response.status_code == 400


def test_login(client):
    client.post(
        "/api/v1/auth/register",
        json={"username": "loginuser", "password": "Test1234", "confirm_password": "Test1234"},
    )
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "loginuser", "password": "Test1234"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_login_wrong_password(client):
    client.post(
        "/api/v1/auth/register",
        json={"username": "wronguser", "password": "Test1234", "confirm_password": "Test1234"},
    )
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "wronguser", "password": "wrong"},
    )
    assert response.status_code == 400


def test_get_me(client, auth_headers):
    response = client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"


def test_change_password(client, auth_headers):
    response = client.post(
        "/api/v1/auth/change-password",
        headers=auth_headers,
        json={"old_password": "Test1234", "new_password": "NewPass5678", "confirm_password": "NewPass5678"},
    )
    assert response.status_code == 200
