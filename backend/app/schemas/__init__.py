
from app.schemas.auth import (
    UserRegister,
    UserLogin,
    UserResponse,
    TokenResponse,
    AuthResponse,
)

from app.schemas.movie import (
    GenreResponse,
    MovieBase,
    MovieResponse,
    MovieListResponse,
)

from app.schemas.watchlist import (
    WatchlistCreate,
    WatchlistResponse,
    WatchlistListResponse,
)

from app.schemas.rating import (
    RatingCreate,
    RatingResponse,
    RatingListResponse,
)

__all__ = [
    "UserRegister",
    "UserLogin",
    "UserResponse",
    "TokenResponse",
    "AuthResponse",
    "GenreResponse",
    "MovieBase",
    "MovieResponse",
    "MovieListResponse",
    "WatchlistCreate",
    "WatchlistResponse",
    "WatchlistListResponse",
    "RatingCreate",
    "RatingResponse",
    "RatingListResponse",
]
