
from sqlalchemy import (
    Column,
    Integer,
    Text,
    DateTime,
    ForeignKey,
    CheckConstraint,
    UniqueConstraint,
    Index,
    func,
)
from sqlalchemy.orm import relationship

from app.database import Base


class UserRating(Base):
    __tablename__ = "user_ratings"

    rating_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False
    )

    movie_id = Column(
        Integer,
        ForeignKey("movies.movie_id", ondelete="RESTRICT"),
        nullable=False
    )

    rating_score = Column(Integer, nullable=False)
    review_text = Column(Text, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp()
    )

    user = relationship("User", back_populates="ratings")
    movie = relationship("Movie", back_populates="ratings")

    __table_args__ = (
        CheckConstraint(
            "rating_score BETWEEN 1 AND 5",
            name="check_user_rating_score"
        ),
        UniqueConstraint(
            "user_id",
            "movie_id",
            name="uq_user_ratings_user_movie"
        ),
        Index("idx_user_ratings_movie_id", "movie_id"),
    )
