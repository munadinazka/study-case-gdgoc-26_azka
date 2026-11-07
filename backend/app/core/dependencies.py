
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.core.security import decode_access_token


bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token tidak valid atau sudah kedaluwarsa.",
        headers={"WWW-Authenticate": "Bearer"}
    )

    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise credentials_exception

    try:
        user_id = int(payload.get("sub"))
    except (ValueError, TypeError):
        raise credentials_exception

    user = (
        db.query(User)
        .filter(User.user_id == user_id)
        .first()
    )

    if user is None:
        raise credentials_exception

    return user
