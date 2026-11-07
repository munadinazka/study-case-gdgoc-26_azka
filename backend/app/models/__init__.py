
from app.models.movie_genre import movie_genre

from app.models.user import User
from app.models.movie import Movie
from app.models.genre import Genre
from app.models.person import Person
from app.models.movie_person import MoviePerson
from app.models.watchlist import Watchlist
from app.models.user_rating import UserRating

__all__ = [
    "User",
    "Movie",
    "Genre",
    "Person",
    "MoviePerson",
    "Watchlist",
    "UserRating",
    "movie_genre",
]
