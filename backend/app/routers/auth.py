
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.auth import (
    UserRegister,
    UserLogin,
    UserResponse,
    AuthResponse,
)
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    user_data: UserRegister,
    db: Session = Depends(get_db),
):
    username = user_data.username.strip()
    email = str(user_data.email).lower()

    if len(username) < 3:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Username minimal 3 karakter.",
        )

    existing_username = (
        db.query(User)
        .filter(User.username == username)
        .first()
    )

    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username sudah digunakan.",
        )

    existing_email = (
        db.query(User)
        .filter(func.lower(User.email) == email)
        .first()
    )

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email sudah terdaftar.",
        )

    new_user = User(
        username=username,
        email=email,
        password_hash=hash_password(user_data.password),
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username atau email sudah digunakan.",
        )

    return new_user


@router.post(
    "/login",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
)
def login(
    user_data: UserLogin,
    db: Session = Depends(get_db),
):
    email = str(user_data.email).lower()

    user = (
        db.query(User)
        .filter(func.lower(User.email) == email)
        .first()
    )

    if user is None or not verify_password(
        user_data.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email atau password salah.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(user.user_id)

    return {
        "token": token,
        "user": user,
    }
