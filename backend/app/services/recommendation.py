import json
import os
import logging

from google import genai
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session, selectinload

from app.models.movie import Movie


logger = logging.getLogger(__name__)


class GeminiRecommendation(BaseModel):
    movie_id: int = Field(
        description="ID film yang dipilih dari katalog film yang tersedia."
    )
    reasoning: str = Field(
        description="Alasan mengapa film tersebut cocok dengan preferensi pengguna."
    )


def generate_movie_recommendation(
    db: Session,
    user_prompt: str
) -> GeminiRecommendation:

    api_key = os.getenv("GEMINI_API_KEY")
    model_name = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")

    if not api_key:
        raise RuntimeError("GEMINI_API_KEY belum dikonfigurasi.")

    # 1. Ambil katalog film dari PostgreSQL.
    movies = (
        db.query(Movie)
        .options(selectinload(Movie.genres))
        .order_by(Movie.movie_id)
        .all()
    )

    if not movies:
        raise ValueError("Belum ada film di database.")

    # 2. Siapkan katalog film untuk diberikan kepada Gemini.
    movie_catalog = []

    for movie in movies:
        movie_catalog.append({
            "movie_id": movie.movie_id,
            "title": movie.title,
            "release_year": movie.release_year,
            "duration_minutes": movie.duration_minutes,
            "average_rating": float(movie.average_rating),
            "genres": [
                genre.genre_name for genre in movie.genres
            ],
            "synopsis": movie.synopsis
        })

    allowed_movie_ids = {
        movie.movie_id for movie in movies
    }

    # 3. Susun instruksi untuk Gemini.
    prompt = f"""
    You are a movie recommendation assistant for FilmLog.

    Your task is to recommend exactly ONE movie from the
    provided movie catalog based on the user's preferences.

    STRICT RULES:
    1. Only recommend movies in the provided catalog.
    2. Never invent a movie or movie_id.
    3. Return the exact movie_id from the catalog.
    4. Explain why the movie matches the user's preferences.
    5. Write the reasoning in Indonesian.
    6. If multiple movies match, choose the most relevant one.

    USER PREFERENCES:
    {user_prompt}

    AVAILABLE MOVIE CATALOG:
    {json.dumps(movie_catalog, ensure_ascii=False, indent=2)}
    """

    # 4. Hubungkan dengan Gemini.
    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_json_schema": (
                GeminiRecommendation.model_json_schema()
            )
        }
    )

    if not response.text:
        raise RuntimeError("Gemini tidak menghasilkan respons.")

    # 5. Validasi struktur hasil Gemini.
    recommendation = GeminiRecommendation.model_validate_json(
        response.text
    )

    # 6. Validasi bahwa ID film benar-benar ada di katalog.
    if recommendation.movie_id not in allowed_movie_ids:
        raise RuntimeError(
            "Gemini menghasilkan movie_id yang tidak tersedia."
        )

    return recommendation