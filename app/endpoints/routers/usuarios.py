from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, Path
from sqlalchemy import select

from ...schemas.user import User, UserCreate
from ...models import (
    User as dbUser,
    Organizacion as dbOrganizacion,
    OrganizacionUsuario as dbOrganizacionUsuario,
)

from ..dependencies.database import sessionDep
from ..dependencies.password import Argon2Hashser
from ..dependencies.auth import userDep

router = APIRouter()
user_id_metadata = {
    "title": "Usuario id",
    "description": "The unique identifier for the Usuario.",
}


@router.post("", response_model=User)
async def create_usuario(new_user: UserCreate, db: sessionDep):
    """
    Create a new Usuario.
    """
    hashed_password = Argon2Hashser.create_hash(new_user.password)
    user = dbUser(**new_user.model_dump(exclude="password"), password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/me", response_model=User)
async def get_me(current_user: userDep, db: sessionDep):
    """
    Get information for the current User.
    """
    me = db.get(dbUser, current_user)
    return me


@router.get("/me/organizaciones")
async def get_my_organizaciones(db: sessionDep, current_user: userDep):
    """
    Get information for the current User.
    """
    subquery = (
        select(dbOrganizacionUsuario.organizacion_id)
        .where(dbOrganizacionUsuario.usuario_id == current_user)
        .subquery()
    )
    query = select(dbOrganizacion).join(subquery)
    organizaciones = db.scalars(query).fetchall()
    return organizaciones


@router.get("/{user_id}", operation_id="get_user", response_model=User)
async def get_usuario(
    user_id: Annotated[UUID, Path(**user_id_metadata)],
    db: sessionDep,
    current_user: userDep,
):
    """
    Get information about a specific Usuario.
    """
    query = select(dbUser).where(dbUser.user_id == user_id)
    user = db.scalars(query).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
