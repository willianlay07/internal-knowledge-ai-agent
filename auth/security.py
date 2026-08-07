from config import (
    JWT_SECRET_KEY,
    JWT_ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

from pwdlib import PasswordHash
password_hasher = PasswordHash.recommended()

import jwt
from jwt.exceptions import InvalidTokenError

from typing import Any
from datetime import datetime, timezone, timedelta

def utc_now() -> str:
    return datetime.now(timezone.utc)

def hash_password(
    plain_password: str
) -> str:
    return password_hasher.hash(plain_password)

def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    return password_hasher.verify(
        plain_password,
        hashed_password
    )

def create_access_token(
    user_id: int
) -> dict[str, Any] | None:
    now = utc_now()
    exp = now + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": exp
    }

    return jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM
    )

def decode_access_token(
    token: str
) -> dict[str, Any] | None:
    try:
        return jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
            options={
                "require": [
                    "sub",
                    "iat",
                    "exp"
                ]
            }
        )

    except InvalidTokenError:
        return None