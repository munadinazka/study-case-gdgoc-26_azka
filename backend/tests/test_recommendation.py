
from unittest.mock import patch

from app.models.movie import Movie


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


def test_recommendation_success(client, db_session):
    create_test_movie(db_session)

    with patch(
        "app.routers.movies.generate_movie_recommendation"
    ) as mock_recommendation:

        mock_recommendation.return_value = {
            "movie_id": 1,
            "reasoning": (
                "Inception cocok karena memiliki alur "
                "cerita yang kompleks dan menarik."
            )
        }

        response = client.post(
            "/api/movies/recommend",
            json={
                "prompt": "Saya suka film dengan cerita kompleks."
            }
        )

    assert response.status_code == 200

    data = response.json()

    assert data["movie_id"] == 1
    assert "reasoning" in data
    assert len(data["reasoning"]) > 0

    mock_recommendation.assert_called_once()


def test_recommendation_returns_existing_movie_id(client, db_session):
    create_test_movie(db_session)

    with patch(
        "app.routers.movies.generate_movie_recommendation"
    ) as mock_recommendation:

        mock_recommendation.return_value = {
            "movie_id": 1,
            "reasoning": "Film tersedia dalam katalog."
        }

        response = client.post(
            "/api/movies/recommend",
            json={"prompt": "Rekomendasikan film bagus."}
        )

    assert response.status_code == 200

    movie_ids = {
        movie.movie_id
        for movie in db_session.query(Movie).all()
    }

    assert response.json()["movie_id"] in movie_ids


def test_recommendation_empty_prompt(client):
    response = client.post(
        "/api/movies/recommend",
        json={"prompt": ""}
    )

    assert response.status_code == 422


def test_recommendation_prompt_too_short(client):
    response = client.post(
        "/api/movies/recommend",
        json={"prompt": "ab"}
    )

    assert response.status_code == 422


def test_recommendation_prompt_too_long(client):
    response = client.post(
        "/api/movies/recommend",
        json={"prompt": "a" * 1001}
    )

    assert response.status_code == 422


def test_recommendation_no_movies_available(client):
    with patch(
        "app.routers.movies.generate_movie_recommendation"
    ) as mock_recommendation:

        mock_recommendation.side_effect = ValueError(
            "Belum ada film di database."
        )

        response = client.post(
            "/api/movies/recommend",
            json={"prompt": "Saya suka film fiksi ilmiah."}
        )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "Belum ada film di database."
    )


def test_recommendation_gemini_error(client):
    with patch(
        "app.routers.movies.generate_movie_recommendation"
    ) as mock_recommendation:

        mock_recommendation.side_effect = RuntimeError(
            "Gemini tidak menghasilkan respons."
        )

        response = client.post(
            "/api/movies/recommend",
            json={"prompt": "Saya suka film fiksi ilmiah."}
        )

    assert response.status_code == 502

    assert response.json()["detail"] == (
        "Gagal mendapatkan rekomendasi film dari AI."
    )
