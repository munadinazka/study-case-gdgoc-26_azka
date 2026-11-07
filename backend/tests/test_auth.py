
from app.models.user import User
from app.core.security import verify_password


REGISTER_URL = "/api/auth/register"
LOGIN_URL = "/api/auth/login"


def register_payload():
    return {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "TestPassword123!",
    }


def test_register_success(client, db_session):
    payload = register_payload()

    response = client.post(REGISTER_URL, json=payload)

    assert response.status_code == 201

    data = response.json()

    assert data["username"] == payload["username"]
    assert data["email"] == payload["email"]
    assert "user_id" in data
    assert "password" not in data
    assert "password_hash" not in data

    # Verify that the password is stored as a hash.
    saved_user = (
        db_session.query(User)
        .filter(User.email == payload["email"])
        .first()
    )

    assert saved_user is not None
    assert saved_user.password_hash != payload["password"]
    assert verify_password(
        payload["password"],
        saved_user.password_hash,
    )


def test_register_duplicate_username(client):
    payload = register_payload()

    first_response = client.post(REGISTER_URL, json=payload)
    assert first_response.status_code == 201

    duplicate_payload = {
        "username": payload["username"],
        "email": "another@example.com",
        "password": "AnotherPassword123!",
    }

    response = client.post(
        REGISTER_URL,
        json=duplicate_payload,
    )

    assert response.status_code == 409


def test_register_duplicate_email(client):
    payload = register_payload()

    first_response = client.post(REGISTER_URL, json=payload)
    assert first_response.status_code == 201

    duplicate_payload = {
        "username": "anotheruser",
        "email": payload["email"],
        "password": "AnotherPassword123!",
    }

    response = client.post(
        REGISTER_URL,
        json=duplicate_payload,
    )

    assert response.status_code == 409


def test_register_invalid_email(client):
    payload = register_payload()
    payload["email"] = "not-an-email"

    response = client.post(REGISTER_URL, json=payload)

    assert response.status_code == 422


def test_register_short_password(client):
    payload = register_payload()
    payload["password"] = "123"

    response = client.post(REGISTER_URL, json=payload)

    assert response.status_code == 422


def test_login_success(client):
    payload = register_payload()

    register_response = client.post(
        REGISTER_URL,
        json=payload,
    )
    assert register_response.status_code == 201

    login_response = client.post(
        LOGIN_URL,
        json={
            "email": payload["email"],
            "password": payload["password"],
        },
    )

    assert login_response.status_code == 200

    data = login_response.json()

    assert "token" in data
    assert isinstance(data["token"], str)
    assert len(data["token"]) > 0

    assert data["user"]["username"] == payload["username"]
    assert data["user"]["email"] == payload["email"]

    assert "password" not in data["user"]
    assert "password_hash" not in data["user"]


def test_login_wrong_password(client):
    payload = register_payload()

    client.post(REGISTER_URL, json=payload)

    response = client.post(
        LOGIN_URL,
        json={
            "email": payload["email"],
            "password": "WrongPassword123!",
        },
    )

    assert response.status_code == 401


def test_login_unknown_email(client):
    response = client.post(
        LOGIN_URL,
        json={
            "email": "unknown@example.com",
            "password": "TestPassword123!",
        },
    )

    assert response.status_code == 401


def test_login_token_can_access_protected_endpoint(client):
    payload = register_payload()

    client.post(REGISTER_URL, json=payload)

    login_response = client.post(
        LOGIN_URL,
        json={
            "email": payload["email"],
            "password": payload["password"],
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["token"]

    response = client.get(
        "/api/watchlist",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200
