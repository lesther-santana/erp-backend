from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from ..dependencies.database import sessionDep
from ..dependencies.password import Argon2Hashser
from ..dependencies.auth import create_token
from ...schemas.security import BearerToken, AuthRequest
from ...models import User


router = APIRouter()


@router.post("", response_model=BearerToken)
async def create_access_token(data: AuthRequest, db: sessionDep):
    """
    Create a new access token.
    """
    query = select(User).where(User.email == data.email)
    user = db.scalars(query).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    valid = Argon2Hashser.verify(user.password, data.password)
    if not valid:
        raise HTTPException(status_code=401, detail="The provided password is invalid.")
    return create_token(user.usuario_id)
