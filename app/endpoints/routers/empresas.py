from typing import Any, Annotated

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import StaleDataError

from ..dependencies.common import errorResponses
from ..dependencies import auth
from ...database import get_db
from ...models import (
    Empresa as dbEmpresa,
    Cliente as dbCliente,
)
from ...schemas.cliente_empresa import Empresa, EmpresaCreate, EmpresaUpdate
from ...schemas.pagination import PagintationParams, PaginatedResponse


router = APIRouter(responses=errorResponses, dependencies=[Depends(auth.get_user)])
pagintationParams = Annotated[PagintationParams, Depends()]
SessionLocal = Annotated[Session, Depends(get_db)]
empresa_id_metadata = {
    "title": "Empresa RNC",
    "description": "The unique identifier for the Empresa.",
}


@router.get("/{rnc}", response_model=Empresa)
async def get_empresa(
    rnc: str = Path(**empresa_id_metadata), db: Session = Depends(get_db)
):
    """
    Retrieve information about a single Empresa.
    """
    query = select(dbEmpresa).where(dbEmpresa.rnc == rnc)
    empresa = db.scalars(query).first()
    if empresa is None:
        raise HTTPException(status_code=404, detail="Empresa not found")
    return empresa


@router.get("", response_model=PaginatedResponse[Empresa])
async def get_multiple_empresas(params: pagintationParams, db: SessionLocal):
    """
    Retrieve multiple empresas with pagination.
    """
    query = select(dbEmpresa).offset(params.offset).limit(params.limit)
    empresas = db.scalars(query).all()
    response = paginate(params, empresas)
    return response


@router.post("")
async def create_empresa(input_emrpesa: EmpresaCreate, db: SessionLocal):
    """
    Create a new Empresa.
    """
    empresa = dbEmpresa(**input_emrpesa.model_dump(exclude={"relacionados"}))
    query = select(dbCliente).where(
        dbCliente.cliente_id.in_(input_emrpesa.relacionados)
    )
    clientes = db.scalars(query).all()
    for c in clientes:
        empresa.relacionados.add(c)
    db.add(empresa)
    db.commit()
    db.refresh(empresa)
    return empresa


@router.put("/{rnc}")
async def update_empresa(
    updated_empresa: EmpresaUpdate,
    db: SessionLocal,
    rnc: str = Path(**empresa_id_metadata),
):
    """
    Update a specific Empresa.
    """
    try:
        stmt = (
            update(dbEmpresa)
            .where(dbEmpresa.rnc == rnc)
            .values(**updated_empresa.model_dump(exclude_unset=True))
            .returning(dbEmpresa)
        )
        empresa = db.scalars(stmt).first()
        db.commit()
    except StaleDataError:
        raise HTTPException(status_code=404, detail="Empresa not found")
    return empresa


@router.delete("/{rnc}")
async def delete_empresa(
    rnc: str = Path(**empresa_id_metadata), db: Session = Depends(get_db)
):
    """
    Delete a specific Empresa.
    """
    stmt = delete(dbEmpresa).where(dbEmpresa.rnc == rnc).returning(dbEmpresa.rn)
    deleted_empresa = db.scalars(stmt).first()
    if deleted_empresa is None:
        raise HTTPException(status_code=404, detail="Cliente not found")
    db.commit()
    return {"message": f"Empresa rnc={deleted_empresa} deleted successfully"}


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
