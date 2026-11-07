
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models.watchlist import Watchlist
from app.models.movie import Movie
from app.models.user import User
from app.schemas.watchlist import (
    WatchlistCreate,
    WatchlistResponse,
    WatchlistListResponse,
)
from app.core.dependencies import get_current_user


router = APIRouter(
    prefix="/watchlist",
    tags=["Watchlist"]
)


@router.get(
    "",
    response_model=WatchlistListResponse,
    status_code=status.HTTP_200_OK
)
def get_watchlist(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    watchlists = (
        db.query(Watchlist)
        .options(
            selectinload(Watchlist.movie)
            .selectinload(Movie.genres)
        )
        .filter(Watchlist.user_id == current_user.user_id)
        .order_by(Watchlist.added_at.desc())
        .all()
    )

    return {
        "watchlists": watchlists,
        "total": len(watchlists)
    }


@router.post(
    "",
    response_model=WatchlistResponse,
    status_code=status.HTTP_201_CREATED
)
def add_to_watchlist(
    watchlist_data: WatchlistCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    movie = (
        db.query(Movie)
        .filter(Movie.movie_id == watchlist_data.movie_id)
        .first()
    )

    if movie is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Film tidak ditemukan."
        )

    existing_watchlist = (
        db.query(Watchlist)
        .filter(
            Watchlist.user_id == current_user.user_id,
            Watchlist.movie_id == watchlist_data.movie_id
        )
        .first()
    )

    if existing_watchlist:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Film sudah ada di watchlist."
        )

    new_watchlist = Watchlist(
        user_id=current_user.user_id,
        movie_id=watchlist_data.movie_id
    )

    try:
        db.add(new_watchlist)
        db.commit()
        db.refresh(new_watchlist)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Film sudah ada di watchlist."
        )

    return new_watchlist


@router.delete(
    "/{movie_id}",
    status_code=status.HTTP_200_OK
)
def remove_from_watchlist(
    movie_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    watchlist_item = (
        db.query(Watchlist)
        .filter(
            Watchlist.user_id == current_user.user_id,
            Watchlist.movie_id == movie_id
        )
        .first()
    )

    if watchlist_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Film tidak ditemukan di watchlist."
        )

    db.delete(watchlist_item)
    db.commit()

    return {
        "message": "Film berhasil dihapus dari watchlist."
    }
