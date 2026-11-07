
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Person(Base):
    __tablename__ = "people"

    person_id = Column(Integer, primary_key=True, autoincrement=True)
    person_name = Column(String(150), nullable=False, unique=True)

    credits = relationship("MoviePerson", back_populates="person")
