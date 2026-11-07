
from app.models.user import User
from app.models.movie import Movie
from app.models.user_rating import UserRating
from app.core.security import hash_password, create_access_token


def create_test_user(
    db_session,
    username="watcheduser",
    email="watched@example.com"
):
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


def test_get_watched_requires_authentication(client):
    response = client.get("/api/watched")

    assert response.status_code == 401


def test_get_watched_empty(client, db_session):
    user = create_test_user(db_session)

    response = client.get(
        "/api/watched",
        headers=get_auth_headers(user)
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 0
    assert data["ratings"] == []


def test_add_watched_success(client, db_session):
    user = create_test_user(db_session)
    create_test_movie(db_session)

    response = client.post(
        "/api/watched",
        json={
            "movieId": 1,
            "rating": 5,
            "review": "Film yang sangat menarik!"
        },
        headers=get_auth_headers(user)
    )

    assert response.status_code == 201

    data = response.json()

    assert data["movie_id"] == 1
    assert data["rating_score"] == 5
    assert data["review_text"] == "Film yang sangat menarik!"
    assert data["movie"]["title"] == "Inception"
    assert "rating_id" in data
    assert "created_at" in data


def test_add_watched_with_snake_case(client, db_session):
    user = create_test_user(db_session)
    create_test_movie(db_session)

    response = client.post(
        "/api/watched",
        json={
            "movie_id": 1,
            "rating_score": 4,
            "review_text": "Ceritanya bagus."
        },
        headers=get_auth_headers(user)
    )

    assert response.status_code == 201

    data = response.json()

    assert data["movie_id"] == 1
    assert data["rating_score"] == 4
    assert data["review_text"] == "Ceritanya bagus."


def test_add_duplicate_watched_movie(client, db_session):
    user = create_test_user(db_session)
    create_test_movie(db_session)

    headers = get_auth_headers(user)

    payload = {
        "movie_id": 1,
        "rating_score": 5,
        "review_text": "Film bagus."
    }

    first_response = client.post(
        "/api/watched",
        json=payload,
        headers=headers
    )

    assert first_response.status_code == 201

    duplicate_response = client.post(
        "/api/watched",
        json=payload,
        headers=headers
    )

    assert duplicate_response.status_code == 409


def test_add_watched_nonexistent_movie(client, db_session):
    user = create_test_user(db_session)

    response = client.post(
        "/api/watched",
        json={
            "movie_id": 9999,
            "rating_score": 5,
            "review_text": "Film bagus."
        },
        headers=get_auth_headers(user)
    )

    assert response.status_code == 404


def test_add_watched_invalid_rating(client, db_session):
    user = create_test_user(db_session)
    create_test_movie(db_session)

    for invalid_rating in [0, 6]:
        response = client.post(
            "/api/watched",
            json={
                "movie_id": 1,
                "rating_score": invalid_rating,
                "review_text": "Film bagus."
            },
            headers=get_auth_headers(user)
        )

        assert response.status_code == 422


def test_add_watched_empty_review(client, db_session):
    user = create_test_user(db_session)
    create_test_movie(db_session)

    response = client.post(
        "/api/watched",
        json={
            "movie_id": 1,
            "rating_score": 5,
            "review_text": "   "
        },
        headers=get_auth_headers(user)
    )

    assert response.status_code == 422


def test_watched_is_user_specific(client, db_session):
    user_1 = create_test_user(db_session)

    user_2 = create_test_user(
        db_session,
        username="anotherwatcheduser",
        email="anotherwatched@example.com"
    )

    create_test_movie(db_session)

    headers_1 = get_auth_headers(user_1)
    headers_2 = get_auth_headers(user_2)

    add_response = client.post(
        "/api/watched",
        json={
            "movieId": 1,
            "rating": 5,
            "review": "Sangat bagus!"
        },
        headers=headers_1
    )

    assert add_response.status_code == 201

    user_1_response = client.get(
        "/api/watched",
        headers=headers_1
    )

    user_2_response = client.get(
        "/api/watched",
        headers=headers_2
    )

    assert user_1_response.status_code == 200
    assert user_2_response.status_code == 200

    assert user_1_response.json()["total"] == 1
    assert user_2_response.json()["total"] == 0
