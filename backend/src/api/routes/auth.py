from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas.user import UserCreate, UserLogin, UserResponse
from src.config import get_settings
from src.core.models import User
from src.infrastructure.database import get_db
from src.utils.auth import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, verify_access_token
from src.utils.security import get_password_hash, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """Helper to get a user by email."""
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalars().first()


async def get_user_by_id(db: AsyncSession, user_id: str) -> User | None:
    """Helper to get a user by ID."""
    result = await db.execute(select(User).filter(User.id == user_id))
    return result.scalars().first()


async def get_token_from_cookie(request: Request) -> str:
    """Dependency to extract the access token from an HttpOnly cookie."""
    token = request.cookies.get("access_token")
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # The token stored in the cookie will have "Bearer " prefix if it was set that way initially.
    # We remove it here. However, I'm updating login_for_access_token to not add it.
    # If the old cookie format exists, this will still handle it gracefully.
    if token.startswith("Bearer "):
        return token[7:]
    return token


async def get_current_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    token: Annotated[str, Depends(get_token_from_cookie)],  # Changed from oauth2_scheme
) -> User:
    """Dependency to get the current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = verify_access_token(token, credentials_exception)
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    user = await get_user_by_id(db, user_id)
    if user is None:
        raise credentials_exception
    return user


@router.post(
    "/register-secret-7x9k2m4n", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register_user(
    user_in: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    registration_token: str | None = None,
):
    """Register a new user. Requires a valid registration token.

    This endpoint is intentionally obscured and requires a secret token
    to prevent unauthorized registrations.
    """
    # Validate registration token
    if not registration_token or registration_token != settings.registration_secret:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid or missing registration token"
        )

    existing_user = await get_user_by_email(db, user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    # Validate email format more strictly
    if not user_in.email or "@" not in user_in.email or "." not in user_in.email.split("@")[1]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email format")

    # Validate password strength
    if len(user_in.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long",
        )

    hashed_password = get_password_hash(user_in.password)
    user = User(email=user_in.email, hashed_password=hashed_password)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/login")
async def login_for_access_token(
    response: Response, user_in: UserLogin, db: Annotated[AsyncSession, Depends(get_db)]
):
    """Login a user and return an access token via HttpOnly cookie."""
    user = await get_user_by_email(db, user_in.email)
    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )

    response.set_cookie(
        key="access_token",
        value=access_token,  # Removed "Bearer " prefix
        httponly=True,
        samesite="lax",  # Strict, Lax, None
        secure=not settings.debug,  # Should be True in production (HTTPS)
        max_age=access_token_expires.total_seconds(),  # cookie expiration in seconds
    )
    return {"message": "Logged in successfully"}


@router.post("/logout")
async def logout(response: Response, current_user: Annotated[User, Depends(get_current_user)]):
    """Logout a user by clearing the HttpOnly cookie."""
    response.delete_cookie(key="access_token")
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    """Get current authenticated user."""
    return current_user
