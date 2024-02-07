from typing import Any, Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.orm.exc import StaleDataError

from ..dependencies import auth
from ..dependencies.common import errorResponses
from ...database import get_db
from ...models import Cliente as dbCliente
from ...schemas.cliente_empresa import Cliente, ClienteCreate, ClienteUpdate
from ...schemas.pagination import PagintationParams, PaginatedResponse


router = APIRouter(responses=errorResponses, dependencies=[Depends(auth.get_user)])

client_id_metadata = {
    "title": "Client ID",
    "description": "The unique identifier for the client.",
}

pagintationParams = Annotated[PagintationParams, Depends()]
SessionLocal = Annotated[Session, Depends(get_db)]


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


@router.get("/{cliente_id}")
async def get_client(
    cliente_id: Annotated[UUID, Path(**client_id_metadata)],
    db: Session = Depends(get_db),
):
    """
    Retrieve information about a specific client.
    """

    load_empresas = selectinload(dbCliente.empresas)
    query = (
        select(dbCliente)
        .options(load_empresas)
        .where(dbCliente.cliente_id == cliente_id)
    )
    cliente = db.scalars(query).first()
    if cliente is None:
        raise HTTPException(status_code=404, detail="Client not found")
    return cliente


@router.get("")
async def get_multiple_clients(
    params: pagintationParams, db: SessionLocal
) -> PaginatedResponse[Cliente]:
    """
    Retrieve information about multiple client.
    """
    query = select(dbCliente).offset(params.offset).limit(params.limit)
    clients = db.scalars(query).all()
    response = paginate(params, clients)
    return response


@router.post("")
async def create_client(input_cliente: ClienteCreate, db: Session = Depends(get_db)):
    """
    Create a new client.
    """
    cliente = dbCliente(**input_cliente.model_dump())
    db.add(cliente)
    db.commit()
    db.refresh(cliente)
    return cliente


@router.put("/{cliente_id}")
async def update_client(
    updated_client: ClienteUpdate,
    db: Session = Depends(get_db),
    cliente_id: UUID = Path(**client_id_metadata),
):
    """
    Update information about a specific client.
    """
    try:
        stmt = (
            update(dbCliente)
            .where(dbCliente.cliente_id == updated_client)
            .values(**updated_client.model_dump(exclude_unset=True))
            .returning(dbCliente)
        )
        cliente = db.scalars(stmt).first()
        db.commit()
    except StaleDataError:
        raise HTTPException(status_code=404, detail="A Tag was not found")
    return cliente


@router.delete("/{cliente_id}")
async def delete_client(
    cliente_id: UUID = Path(**client_id_metadata), db: Session = Depends(get_db)
):
    """
    Delete a specific client.
    """
    stmt = (
        delete(dbCliente)
        .where(dbCliente.cliente_id == cliente_id)
        .returning(dbCliente.cliente_id)
    )
    deleted_cliente = db.scalars(stmt).first()
    if deleted_cliente is None:
        raise HTTPException(status_code=404, detail="Cliente not found")
    db.commit()
    return {"message": f"Cliente id={deleted_cliente} deleted successfully"}
