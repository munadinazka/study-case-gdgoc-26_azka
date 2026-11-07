
from sqlalchemy import (
    Column,
    Integer,
    String,
    SmallInteger,
    ForeignKey,
    CheckConstraint,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.database import Base


class MoviePerson(Base):
    __tablename__ = "movie_people"

    movie_credit_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    movie_id = Column(
        Integer,
        ForeignKey("movies.movie_id", ondelete="CASCADE"),
        nullable=False
    )

    person_id = Column(
        Integer,
        ForeignKey("people.person_id"),
        nullable=False
    )

    role_type = Column(String(10), nullable=False)
    billing_order = Column(SmallInteger, nullable=True)

    movie = relationship("Movie", back_populates="credits")
    person = relationship("Person", back_populates="credits")

    __table_args__ = (
        CheckConstraint(
            "role_type IN ('actor', 'director')",
            name="check_movie_people_role_type"
        ),
        CheckConstraint(
            """
            (role_type = 'actor'
             AND billing_order IS NOT NULL
             AND billing_order > 0)
            OR
            (role_type = 'director'
             AND billing_order IS NULL)
            """,
            name="chk_movie_people_billing_order"
        ),
        UniqueConstraint(
            "movie_id",
            "person_id",
            "role_type",
            name="uq_movie_people_credit"
        ),
    )
