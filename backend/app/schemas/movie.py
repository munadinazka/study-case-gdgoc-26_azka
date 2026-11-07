
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class GenreResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    genre_id: int
    genre_name: str


class MovieBase(BaseModel):
    title: str
    release_year: int
    duration_minutes: int
    average_rating: Decimal
    synopsis: str
    poster_url: str


class MovieResponse(MovieBase):
    model_config = ConfigDict(from_attributes=True)

    movie_id: int
    genres: list[GenreResponse] = Field(default_factory=list)
    director: str | None = None
    cast: list[str] = Field(default_factory=list)

class MovieListResponse(BaseModel):
    movies: list[MovieResponse]
    total: int
