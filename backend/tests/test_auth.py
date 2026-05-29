import pytest

def test_register_user(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "strongpassword"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@example.com"
    assert "id" in data

def test_register_existing_user(client, test_user):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "testadmin",
            "email": "another@example.com",
            "password": "password"
        }
    )
    assert response.status_code == 400

def test_login_success(client, test_user):
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "testadmin",
            "password": "password123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client, test_user):
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "testadmin",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401

def test_access_protected_route(client, test_token):
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    assert response.json()["username"] == "testadmin"

def test_access_protected_route_without_token(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
