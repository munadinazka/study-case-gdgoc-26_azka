
from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    AliasChoices,
)

from app.schemas.movie import MovieResponse


class RatingCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    movie_id: int = Field(
        validation_alias=AliasChoices("movie_id", "movieId")
    )

    rating_score: int = Field(
        ge=1,
        le=5,
        validation_alias=AliasChoices("rating_score", "rating")
    )

    review_text: str = Field(
        min_length=1,
        max_length=5000,
        validation_alias=AliasChoices("review_text", "review")
    )


class RatingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    rating_id: int
    movie_id: int
    rating_score: int
    review_text: str
    created_at: datetime
    movie: MovieResponse


class RatingListResponse(BaseModel):
    ratings: list[RatingResponse]
    total: int
