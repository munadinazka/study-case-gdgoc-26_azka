
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models.user import User
from app.models.movie import Movie
from app.models.user_rating import UserRating
from app.schemas.rating import (
    RatingCreate,
    RatingResponse,
    RatingListResponse,
)
from app.core.dependencies import get_current_user


router = APIRouter(
    prefix="/watched",
    tags=["Watched & Reviews"]
)


@router.get(
    "",
    response_model=RatingListResponse,
    status_code=status.HTTP_200_OK
)
def get_watched(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ratings = (
        db.query(UserRating)
        .options(
            selectinload(UserRating.movie)
            .selectinload(Movie.genres)
        )
        .filter(UserRating.user_id == current_user.user_id)
        .order_by(UserRating.created_at.desc())
        .all()
    )

    return {
        "ratings": ratings,
        "total": len(ratings)
    }


@router.post(
    "",
    response_model=RatingResponse,
    status_code=status.HTTP_201_CREATED
)
def add_watched(
    rating_data: RatingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    movie = (
        db.query(Movie)
        .filter(Movie.movie_id == rating_data.movie_id)
        .first()
    )

    if movie is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Film tidak ditemukan."
        )

    existing_rating = (
        db.query(UserRating)
        .filter(
            UserRating.user_id == current_user.user_id,
            UserRating.movie_id == rating_data.movie_id
        )
        .first()
    )

    if existing_rating:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Film sudah tercatat dalam riwayat tontonan."
        )

    new_rating = UserRating(
        user_id=current_user.user_id,
        movie_id=rating_data.movie_id,
        rating_score=rating_data.rating_score,
        review_text=rating_data.review_text.strip()
    )

    if not new_rating.review_text:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Review tidak boleh kosong."
        )

    try:
        db.add(new_rating)
        db.commit()
        db.refresh(new_rating)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Film sudah tercatat dalam riwayat tontonan."
        )

    return new_rating
