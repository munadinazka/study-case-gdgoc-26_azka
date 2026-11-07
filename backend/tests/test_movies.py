
from decimal import Decimal

from app.models.movie import Movie
from app.models.genre import Genre


def create_test_movies(db_session):
    """Create sample movies and genres for testing."""

    action = Genre(genre_name="Action")
    science_fiction = Genre(genre_name="Science Fiction")

    movie_1 = Movie(
        movie_id=2,
        title="The Matrix",
        release_year=1999,
        duration_minutes=136,
        average_rating=Decimal("8.7"),
        synopsis="A computer hacker discovers the truth about reality.",
        poster_url="https://example.com/matrix.jpg",
        genres=[action, science_fiction],
    )

    movie_2 = Movie(
        movie_id=1,
        title="Inception",
        release_year=2010,
        duration_minutes=148,
        average_rating=Decimal("8.8"),
        synopsis="A thief enters people's dreams to steal information.",
        poster_url="https://example.com/inception.jpg",
        genres=[science_fiction],
    )

    db_session.add_all([movie_1, movie_2])
    db_session.commit()

    return movie_1, movie_2


def test_get_movies_success(client, db_session):
    create_test_movies(db_session)

    response = client.get("/api/movies")

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 2
    assert len(data["movies"]) == 2

    # Verify that movies are sorted by movie_id.
    assert data["movies"][0]["movie_id"] == 1
    assert data["movies"][1]["movie_id"] == 2

    assert data["movies"][0]["title"] == "Inception"


def test_get_movies_empty(client):
    response = client.get("/api/movies")

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 0
    assert data["movies"] == []


def test_get_movie_detail_success(client, db_session):
    create_test_movies(db_session)

    response = client.get("/api/movies/1")

    assert response.status_code == 200

    data = response.json()

    assert data["movie_id"] == 1
    assert data["title"] == "Inception"
    assert data["release_year"] == 2010
    assert data["duration_minutes"] == 148


def test_get_movie_detail_includes_genres(client, db_session):
    create_test_movies(db_session)

    response = client.get("/api/movies/2")

    assert response.status_code == 200

    data = response.json()

    genre_names = [
        genre["genre_name"]
        for genre in data["genres"]
    ]

    assert "Action" in genre_names
    assert "Science Fiction" in genre_names


def test_get_movie_detail_not_found(client):
    response = client.get("/api/movies/9999")

    assert response.status_code == 404

    assert response.json()["detail"] == "Film tidak ditemukan."


def test_get_movie_detail_invalid_id(client):
    response = client.get("/api/movies/invalid-id")

    assert response.status_code == 422
