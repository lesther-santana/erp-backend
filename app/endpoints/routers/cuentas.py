from typing import Any, Annotated

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from ..dependencies import auth
from ..dependencies.common import errorResponses
from ...database import get_db
from ...models import (
    Servicio as dbServicio,
    Cuenta as dbCuenta,
    Empresa as dbEmpresa,
    CuentaServicio as dbCuentaServicio,
)
from ...schemas.cuenta import CuentaNew
from ...schemas.pagination import PagintationParams, PaginatedResponse


router = APIRouter(responses=errorResponses, dependencies=[Depends(auth.get_user)])
pagintationParams = Annotated[PagintationParams, Depends()]
SessionLocal = Annotated[Session, Depends(get_db)]
cuenta_id_metadata = {
    "title": "Cuenta id",
    "description": "The unique identifier for the Cuenta.",
}


@router.get("/{cuenta_id}")
async def get_tag(
    cuenta_id: int = Path(**cuenta_id_metadata), db: Session = Depends(get_db)
):
    """
    Retrieve information about a single cuenta.
    """
    load_relacionados = selectinload(dbCuenta.empresa).subqueryload(
        dbEmpresa.relacionados
    )
    query = (
        select(dbCuenta)
        .options(load_relacionados)
        .where(dbCuenta.cuenta_id == cuenta_id)
    )
    cuenta = db.scalars(query).first()
    if cuenta is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    cuenta.empresa
    return cuenta


@router.get("")
async def get_cuentas(params: pagintationParams, db: SessionLocal):
    """
    Retrieve a multiple cuentas with pagination.
    """
    load_relacionados = selectinload(dbCuenta.empresa).subqueryload(
        dbEmpresa.relacionados
    )
    load_servicios = selectinload(dbCuenta.servicios).subqueryload(dbServicio.tags)
    query = (
        select(dbCuenta)
        .options(load_relacionados)
        .options(load_servicios)
        .offset(params.offset)
        .limit(params.limit)
    )
    cuentas = db.scalars(query).all()
    # response = paginate(params, cuentas)
    return cuentas


@router.post("")
async def create_cuenta(new_cuenta: CuentaNew, db: SessionLocal):
    """
    Create a new cuenta.
    """
    try:
        cuenta = dbCuenta(**new_cuenta.model_dump(exclude=["servicios"]))
        query = select(dbServicio).where(
            dbServicio.servicio_id.in_(new_cuenta.servicios)
        )
        servicios = db.scalars(query).all()
        all_services_exist = len(servicios) == len(new_cuenta.servicios)
        if not all_services_exist:
            raise HTTPException(status_code=404, detail="Some services were not found")
        for s in servicios:
            cuenta_servicio = dbCuentaServicio(servicio_id=s.servicio_id)
            cuenta.cuenta_servicios.append(cuenta_servicio)
        db.add(cuenta)
        db.commit()
        db.refresh(cuenta)
    except IntegrityError:
        raise HTTPException(
            status_code=422, detail="Empresa cannot have multiple cuentas"
        )
    return cuenta


@router.delete("/{cuenta_id}")
async def delete_cuenta(
    cuenta_id: int = Path(**cuenta_id_metadata), db: Session = Depends(get_db)
):
    """
    Delete a specific cuenta.
    """
    stmt = (
        delete(dbCuenta)
        .where(dbCuenta.cuenta_id == cuenta_id)
        .returning(dbCuenta.cuenta_id)
    )
    deleted_cuenta = db.scalars(stmt).first()
    if deleted_cuenta is None:
        raise HTTPException(status_code=404, detail=f"Tag id={cuenta_id} not found")
    db.commit()
    return {"message": f"Servicio id={deleted_cuenta} deleted successfully"}


def paginate(pagination_parms: PagintationParams, data: list[Any]):
    """Build Paginataded Response"""
    response = PaginatedResponse(
        total=len(data),
        offset=pagination_parms.offset,
        limit=pagination_parms.limit,
        items=data,
    )
    if len(data) == pagination_parms.limit:
        response.next_offset = pagination_parms.offset + pagination_parms.offset
    return response
