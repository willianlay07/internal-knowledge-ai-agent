from fastapi import (
    APIRouter,
    status,
    HTTPException,
    Depends
)
from typing import Annotated, Any

from schemas import (
    RegisterRequest,
    UserResponse,
    TokenResponse
)

from sqlite_db import create_user, get_user_by_email
from auth.security import hash_password, verify_password, create_access_token
from auth.dependencies import get_current_user

from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(
    prefix="/auth",
    tags=["Authenticate"]
)

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register(
    request: RegisterRequest
):
    user = create_user(str(request.email), hash_password(request.password))

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists."
        )

    return UserResponse(
        id=user["id"],
        email=user["email"],
        created_at=user["created_at"]
    )

@router.post(
    "/login",
    response_model=TokenResponse
)
def login(
    form_data: Annotated[
        OAuth2PasswordRequestForm,
        Depends()
    ]
):
    user = get_user_by_email(form_data.username)

    if user is None or not verify_password(form_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return TokenResponse(
        access_token=create_access_token(user["id"]),
        token_type="Bearer"
    )

@router.get(
    "/me",
    response_model=UserResponse
)
def getMe(
    current_user: Annotated[
        dict,
        Depends(get_current_user)
    ]
):
    return UserResponse(
        id=current_user["id"],
        email=current_user["email"],
        created_at=current_user["created_at"]
    )