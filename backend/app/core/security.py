
from datetime import datetime, timedelta, timezone
import os

import jwt
from dotenv import load_dotenv
from pwdlib import PasswordHash
from jwt.exceptions import InvalidTokenError


load_dotenv()

# Password hashing menggunakan Argon2
password_hash = PasswordHash.recommended()


# JWT configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "60")
)

if not JWT_SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY belum diatur di file .env")


def hash_password(password: str) -> str:
    """Mengubah password asli menjadi hash Argon2."""
    return password_hash.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    """Memeriksa password dengan hash yang tersimpan."""
    return password_hash.verify(plain_password, hashed_password)


def create_access_token(user_id: int) -> str:
    """Membuat JWT untuk pengguna yang berhasil login."""

    now = datetime.now(timezone.utc)

    expire = now + timedelta(
        minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": expire,
    }

    token = jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM
    )

    return token


def decode_access_token(token: str) -> dict | None:
    """Memverifikasi JWT dan mengembalikan payload jika valid."""

    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
            options={"require": ["exp", "sub"]}
        )

        # Pastikan subject berisi user ID numerik
        user_id = int(payload["sub"])

        if user_id <= 0:
            return None

        return payload

    except (InvalidTokenError, ValueError, TypeError):
        return None
