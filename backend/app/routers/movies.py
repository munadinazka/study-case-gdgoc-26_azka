import logging

from google.genai import errors as genai_errors
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models.movie import Movie
from app.schemas.movie import MovieResponse, MovieListResponse
from app.models.movie_person import MoviePerson
from app.schemas.recommendation import (
    RecommendationRequest,
    RecommendationResponse,
)
from app.services.recommendation import (
    generate_movie_recommendation,
)

router = APIRouter(
    prefix="/movies",
    tags=["Movies"]
)


@router.get(
    "",
    response_model=MovieListResponse,
    status_code=status.HTTP_200_OK
)
def get_movies(db: Session = Depends(get_db)):
    movies = (
        db.query(Movie)
        .options(
            selectinload(Movie.genres),
            selectinload(Movie.credits).selectinload(MoviePerson.person)
        )
        .order_by(Movie.movie_id.asc())
        .all()
    )

    return {
        "movies": movies,
        "total": len(movies)
    }


@router.get(
    "/{movie_id}",
    response_model=MovieResponse,
    status_code=status.HTTP_200_OK
)
def get_movie_detail(
    movie_id: int,
    db: Session = Depends(get_db)
):
    movie = (
        db.query(Movie)
        .options(
            selectinload(Movie.genres),
            selectinload(Movie.credits).selectinload(MoviePerson.person)
        )
        .filter(Movie.movie_id == movie_id)
        .first()
    )

    if movie is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Film tidak ditemukan."
        )

    return movie

logger = logging.getLogger(__name__)


@router.post(
    "/recommend",
    response_model=RecommendationResponse,
    status_code=200,
)
def recommend_movie(
    request: RecommendationRequest,
    db: Session = Depends(get_db),
):
    try:
        recommendation = generate_movie_recommendation(
            db=db,
            user_prompt=request.prompt,
        )

        return recommendation

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except genai_errors.APIError as error:
        logger.exception("Gemini API error.")

        if error.code == 503:
            raise HTTPException(
                status_code=503,
                detail="Layanan rekomendasi AI sedang sibuk. Silakan coba lagi nanti.",
            )

        raise HTTPException(
            status_code=502,
            detail="Layanan rekomendasi AI sedang bermasalah.",
        )

    except RuntimeError:
        logger.exception("Gemini recommendation failed.")

        raise HTTPException(
            status_code=502,
            detail="Gagal mendapatkan rekomendasi film dari AI.",
        )

    except Exception:
        logger.exception("Unexpected recommendation error.")

        raise HTTPException(
            status_code=500,
            detail="Terjadi kesalahan pada server.",
        )