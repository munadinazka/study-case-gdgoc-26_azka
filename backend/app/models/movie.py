
from sqlalchemy import Column, Integer, String, Text, Numeric
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.movie_genre import movie_genre


class Movie(Base):
    __tablename__ = "movies"

    movie_id = Column(Integer, primary_key=True, autoincrement=False)
    title = Column(String(255), nullable=False)
    release_year = Column(Integer, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    average_rating = Column(Numeric(3, 1), nullable=False)
    synopsis = Column(Text, nullable=False)
    poster_url = Column(Text, nullable=False)

    genres = relationship(
        "Genre",
        secondary=movie_genre,
        back_populates="movies"
    )

    credits = relationship("MoviePerson", back_populates="movie")
    watchlists = relationship("Watchlist", back_populates="movie")
    ratings = relationship("UserRating", back_populates="movie")
    @property
    def director(self):
        for credit in self.credits:
            if credit.role_type == "director":
                return credit.person.person_name
        return None

    @property
    def cast(self):
        actor_credits = [
            credit for credit in self.credits
            if credit.role_type == "actor"
        ]
        actor_credits.sort(
            key=lambda credit: (
                credit.billing_order
                if credit.billing_order is not None
                else 999
            )
        )
        return [credit.person.person_name for credit in actor_credits]