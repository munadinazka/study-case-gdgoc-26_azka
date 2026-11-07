
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.movie_genre import movie_genre


class Genre(Base):
    __tablename__ = "genres"

    genre_id = Column(Integer, primary_key=True, autoincrement=True)
    genre_name = Column(String(50), nullable=False, unique=True)

    movies = relationship(
        "Movie",
        secondary=movie_genre,
        back_populates="genres"
    )
