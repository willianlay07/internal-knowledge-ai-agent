from fastapi import (
    Depends,
    HTTPException,
    status
)
from fastapi.security import OAuth2PasswordBearer

from typing import Annotated, Any
from auth.security import decode_access_token
from sqlite_db import get_user_by_id

oauth2_schema = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)

def get_current_user(
    token: Annotated[
        str,
        Depends(oauth2_schema)
    ],
) -> dict[str, Any]:
    error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired access token.",
        headers={"WWW-Authenticate": "Bearer"}
    )

    payload = decode_access_token(token)
    if payload is None:
        raise error

    try:
        user_id = payload.get("sub")
    except (TypeError, ValueError):
        raise error

    user = get_user_by_id(user_id)
    if user is None:
        raise error

    return user
