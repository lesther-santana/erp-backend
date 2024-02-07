from fastapi import HTTPException, status
from datetime import datetime, timedelta, timezone
from argon2 import PasswordHasher
from jose import JWTError, jwt


SECRET = "supersecret"
ALGORITHM = "HS256"
hasher = PasswordHasher()


def create_token(sub: int | str) -> (str, int):
    """
    Creates JWT token. Returns token and expiration timestamp
    """
    current_time = datetime.now(timezone.utc)
    expiration_time = calcualte_exp_time(current_time)
    claims = {"sub": str(sub), "iat": current_time, "exp": expiration_time}
    access_token = jwt.encode(claims=claims, key=SECRET, algorithm=ALGORITHM)
    return access_token, expiration_time


def calcualte_exp_time(current_time: datetime, delta_minutes: int = 15) -> int:
    exp_datetime = current_time + timedelta(minutes=delta_minutes)
    exp_as_timestamp = exp_datetime.timestamp()
    return int(exp_as_timestamp)


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        user = payload["sub"]
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def create_password_hash(password: str) -> str:
    return hasher.hash(password)


def verify_password(hashed_password: str, password: str) -> bool:
    return hasher.verify(hashed_password, password)
