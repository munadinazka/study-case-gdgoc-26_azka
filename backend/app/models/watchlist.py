
from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship

from app.database import Base


class Watchlist(Base):
    __tablename__ = "watchlists"

    watchlist_id = Column(
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

    added_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp()
    )

    user = relationship("User", back_populates="watchlists")
    movie = relationship("Movie", back_populates="watchlists")

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "movie_id",
            name="uq_watchlists_user_movie"
        ),
    )
