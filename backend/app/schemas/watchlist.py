
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, AliasChoices
from app.schemas.movie import MovieResponse


class WatchlistCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    movie_id: int = Field(
        validation_alias=AliasChoices("movie_id", "movieId")
    )


class WatchlistResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    watchlist_id: int
    movie_id: int
    added_at: datetime
    movie: MovieResponse


class WatchlistListResponse(BaseModel):
    watchlists: list[WatchlistResponse]
    total: int
