
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Index,
    func,
    text,
)
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp()
    )

    watchlists = relationship("Watchlist", back_populates="user")
    ratings = relationship("UserRating", back_populates="user")

    __table_args__ = (
        Index(
            "uq_users_email_lower",
            func.lower(email),
            unique=True
        ),
    )
