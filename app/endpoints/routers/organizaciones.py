from fastapi import APIRouter, HTTPException, Path
from sqlalchemy import select
from uuid import UUID
from typing import Annotated

from ..dependencies.database import sessionDep
from ..dependencies.auth import userDep, superUserDep, forbidden_resource
from ..dependencies.password import Argon2Hashser

from ...schemas.organizacion import Organizacion, OrganizacionCreate, Empleado
from ...models import (
    Organizacion as dbOrganizacion,
    OrganizacionUsuario as dbOrgUsuario,
    User as dbUsuario,
)


extra = {"security": {"bearerAuth": []}}

router = APIRouter()
organizacion_id_metadata = {
    "title": "Organizacion id",
    "description": "The unique identifier for a Organizacion.",
}


@router.post("", response_model=Organizacion)
async def create_organizacion(new_organizacion: OrganizacionCreate, db: sessionDep):
    """
    Create a new organizcion.
    """
    organizacion = dbOrganizacion(**new_organizacion.model_dump())
    # miembro = dbOrgUsuario(usuario_id=current_user.usuario_id)
    # organizacion.organizacion_usuarios.append(miembro)
    db.add(organizacion)
    db.commit()
    db.refresh(organizacion)
    return organizacion


@router.get("")
async def get_my_organizaciones(
    db: sessionDep,
    current_user: userDep,
):
    """
    Retrive information about a specific Organizacion.
    """
    subquery = (
        select(dbOrgUsuario.organizacion_id)
        .where(dbOrgUsuario.usuario_id == current_user)
        .subquery()
    )
    query = select(dbOrganizacion).join(subquery)
    organizaciones = db.scalars(query).fetchall()
    return organizaciones


@router.get("/{organizacion_id}", response_model=Organizacion)
async def get_organizacion(
    db: sessionDep,
    # current_user: CurrentUserDep,
    organizacion_id: Annotated[UUID, Path(**organizacion_id_metadata)],
):
    """
    Retrive information about a specific Organizacion.
    """
    query = select(dbOrganizacion).where(
        dbOrganizacion.organizacion_id == organizacion_id
    )
    organizacion = db.scalars(query).first()
    if organizacion is None:
        raise HTTPException(status_code=404, detail="Organizacion not found")
    return organizacion


@router.post("/{organizacion_id}/users", response_model=Empleado)
async def add_user_to_organizacion(
    db: sessionDep,
    super_user_id: superUserDep,
    organizacion_id: Annotated[UUID, Path(**organizacion_id_metadata)],
    empleado: Empleado,
):
    """
    Add new User to the organizacion.
    """
    exists_criteria = select(dbOrgUsuario).where(
        dbOrgUsuario.organizacion_id == organizacion_id,
        dbOrgUsuario.usuario_id == super_user_id,
    )
    print(super_user_id)
    if db.scalars(exists_criteria).first() is None:
        raise forbidden_resource
    query = select(dbOrganizacion).where(
        dbOrganizacion.organizacion_id == organizacion_id
    )
    organizacion = db.scalars(query).first()
    if organizacion is None:
        raise HTTPException(status_code=404, detail="Organizacion not found")
    password = Argon2Hashser.create_hash(empleado.password)
    user = dbUsuario(
        **empleado.model_dump(exclude=["password"]),
        password=password,
        org=organizacion,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
