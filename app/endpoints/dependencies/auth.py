from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from typing import Annotated
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas.security import BearerToken


from .constants import (
    BEARER_FORMAT,
    AUTH_SCHEME_NAME,
    AUTH_DESCRIPTION,
    JWT_SECRET,
    JWT_ALGORITHM,
)


auth_scheme = HTTPBearer(
    bearerFormat=BEARER_FORMAT,
    scheme_name=AUTH_SCHEME_NAME,
    description=AUTH_DESCRIPTION,
)


missing_token = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="access token missing",
    headers={"WWW-Authenticate": "Bearer"},
)
bad_token_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail="Bad access token"
)
invalid_token = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate token",
    headers={"WWW-Authenticate": "Bearer"},
)
forbidden_resource = HTTPException(status_code=403, detail="Access forbidden")


def parse_auth_header(
    auth_header: Annotated[HTTPAuthorizationCredentials, Depends(auth_scheme)],
) -> dict:
    payload = decode_token(auth_header.credentials)
    return payload


def get_superuser(
    session: Annotated[Session, Depends(get_db)],
    payload: Annotated[str, Depends(parse_auth_header)],
):
    user = session.get(User, payload["sub"])
    if user.rol == "superuser":
        return user.usuario_id


def get_supervisor(
    session: Annotated[Session, Depends(get_db)],
    payload: Annotated[str, Depends(parse_auth_header)],
):
    user = session.get(User, payload["sub"])
    if user.rol == "supervisor":
        return user.usuario_id


def get_user(
    session: Annotated[Session, Depends(get_db)],
    payload: Annotated[str, Depends(parse_auth_header)],
):
    user = session.get(User, payload["sub"])
    return user.usuario_id


def create_token(sub: int | str, exp_time_delta: int = 15) -> BearerToken:
    """Creates JWT token.
    Args:
        sub (str): It refers to the user ID or identifier of the entity the token represents.
        exp_time_delta: specifies the expiration time in minutes on or after which the JWT must not be accepted for processing.

    Returns:
        str: The string representation of the header, claims, and signature.
        int: Expiration timestamp.
    """

    def calcualte_exp_time(
        current_time: datetime, delta_minutes: int = exp_time_delta
    ) -> int:
        exp_datetime = current_time + timedelta(minutes=delta_minutes)
        exp_as_timestamp = exp_datetime.timestamp()
        return int(exp_as_timestamp)

    current_time = datetime.now(timezone.utc)
    expiration_time = calcualte_exp_time(current_time)
    claims = {"sub": str(sub), "iat": current_time, "exp": expiration_time}
    access_token = jwt.encode(claims=claims, key=JWT_SECRET, algorithm=JWT_ALGORITHM)
    token = BearerToken(access_token=access_token, expires_at=expiration_time)
    return token


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except JWTError:
        raise invalid_token
    return payload


userDep = Annotated[str, Depends(get_user)]
superUserDep = Annotated[str, Depends(get_superuser)]
supervisorDep = Annotated[str, Depends(get_supervisor)]
