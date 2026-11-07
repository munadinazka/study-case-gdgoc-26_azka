
from sqlalchemy import Table, Column, Integer, ForeignKey

from app.database import Base


movie_genre = Table(
    "movie_genre",
    Base.metadata,

    Column(
        "movie_id",
        Integer,
        ForeignKey("movies.movie_id", ondelete="CASCADE"),
        primary_key=True
    ),

    Column(
        "genre_id",
        Integer,
        ForeignKey("genres.genre_id", ondelete="CASCADE"),
        primary_key=True
    ),
)
