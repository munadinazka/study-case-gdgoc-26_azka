
from app.models.user import User
from app.models.movie import Movie
from app.models.watchlist import Watchlist
from app.core.security import hash_password, create_access_token


def create_test_user(db_session, username="watchlistuser", email="watchlist@example.com"):
    user = User(
        username=username,
        email=email,
        password_hash=hash_password("TestPassword123!")
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return user


def create_test_movie(db_session, movie_id=1):
    movie = Movie(
        movie_id=movie_id,
        title="Inception",
        release_year=2010,
        duration_minutes=148,
        average_rating=8.8,
        synopsis="A thief enters people's dreams to steal information.",
        poster_url="https://example.com/inception.jpg"
    )

    db_session.add(movie)
    db_session.commit()
    db_session.refresh(movie)

    return movie


def get_auth_headers(user):
    token = create_access_token(user.user_id)

    return {
        "Authorization": f"Bearer {token}"
    }


def test_get_watchlist_requires_authentication(client):
    response = client.get("/api/watchlist")

    assert response.status_code == 401


def test_get_watchlist_empty(client, db_session):
    user = create_test_user(db_session)

    response = client.get(
        "/api/watchlist",
        headers=get_auth_headers(user)
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 0
    assert data["watchlists"] == []


def test_add_to_watchlist_success(client, db_session):
    user = create_test_user(db_session)
    create_test_movie(db_session)

    response = client.post(
        "/api/watchlist",
        json={"movieId": 1},
        headers=get_auth_headers(user)
    )

    assert response.status_code == 201

    data = response.json()

    assert data["movie_id"] == 1
    assert data["movie"]["title"] == "Inception"
    assert "watchlist_id" in data
    assert "added_at" in data


def test_add_duplicate_movie_to_watchlist(client, db_session):
    user = create_test_user(db_session)
    create_test_movie(db_session)

    headers = get_auth_headers(user)

    first_response = client.post(
        "/api/watchlist",
        json={"movie_id": 1},
        headers=headers
    )

    assert first_response.status_code == 201

    duplicate_response = client.post(
        "/api/watchlist",
        json={"movie_id": 1},
        headers=headers
    )

    assert duplicate_response.status_code == 409


def test_add_nonexistent_movie_to_watchlist(client, db_session):
    user = create_test_user(db_session)

    response = client.post(
        "/api/watchlist",
        json={"movie_id": 9999},
        headers=get_auth_headers(user)
    )

    assert response.status_code == 404


def test_remove_from_watchlist_success(client, db_session):
    user = create_test_user(db_session)
    create_test_movie(db_session)

    headers = get_auth_headers(user)

    add_response = client.post(
        "/api/watchlist",
        json={"movie_id": 1},
        headers=headers
    )

    assert add_response.status_code == 201

    delete_response = client.delete(
        "/api/watchlist/1",
        headers=headers
    )

    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == (
        "Film berhasil dihapus dari watchlist."
    )

    remaining_items = (
        db_session.query(Watchlist)
        .filter(
            Watchlist.user_id == user.user_id,
            Watchlist.movie_id == 1
        )
        .all()
    )

    assert len(remaining_items) == 0


def test_remove_nonexistent_watchlist_item(client, db_session):
    user = create_test_user(db_session)

    response = client.delete(
        "/api/watchlist/9999",
        headers=get_auth_headers(user)
    )

    assert response.status_code == 404


def test_watchlist_is_user_specific(client, db_session):
    user_1 = create_test_user(db_session)

    user_2 = create_test_user(
        db_session,
        username="anotheruser",
        email="another@example.com"
    )

    create_test_movie(db_session)

    headers_1 = get_auth_headers(user_1)
    headers_2 = get_auth_headers(user_2)

    add_response = client.post(
        "/api/watchlist",
        json={"movie_id": 1},
        headers=headers_1
    )

    assert add_response.status_code == 201

    user_1_response = client.get(
        "/api/watchlist",
        headers=headers_1
    )

    user_2_response = client.get(
        "/api/watchlist",
        headers=headers_2
    )

    assert user_1_response.status_code == 200
    assert user_2_response.status_code == 200

    assert user_1_response.json()["total"] == 1
    assert user_2_response.json()["total"] == 0
