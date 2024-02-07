from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import StaleDataError
from typing import List, Any, Annotated

from ..dependencies.common import errorResponses
from ..dependencies import auth
from ...models import Servicio as dbServicio, TagServicio as dbTagServicio, Tag as dbTag
from ...database import get_db
from ...schemas.pagination import PagintationParams, PaginatedResponse
from ...schemas.servicio import Servicio, ServicioCreate, ServicioUpdate


router = APIRouter(responses=errorResponses, dependencies=[Depends(auth.get_user)])
pagintationParams = Annotated[PagintationParams, Depends()]
SessionLocal = Annotated[Session, Depends(get_db)]
servicio_id_metadata = {
    "title": "Servicio id",
    "description": "The unique identifier for the Servicio.",
}


@router.get("/{servicio_id}", response_model=Servicio)
async def get_servicio(
    servicio_id: int = Path(**servicio_id_metadata),
    db: Session = Depends(get_db),
):
    """
    Retrieve information about a specific Servicio.
    """
    query = select(dbServicio).where(dbServicio.servicio_id == servicio_id)
    servicio = db.scalars(query).first()
    if servicio is None:
        raise HTTPException(status_code=404, detail="Servicio not found")
    return servicio


@router.get("", response_model=PaginatedResponse[Servicio])
async def get_multiple_servicios(params: pagintationParams, db: SessionLocal):
    """
    Retrieve information about multiple servicios using pagination.
    """
    query = select(dbServicio).offset(params.offset).limit(params.limit)
    servicios = db.scalars(query).all()
    response = paginate(params, servicios)
    return response


@router.post("", response_model=Servicio)
async def create_servicio(new_servicio: ServicioCreate, db: SessionLocal):
    """
    Create a new Servicio.
    """
    servicio = dbServicio(**new_servicio.model_dump(exclude={"tags"}))
    query = select(dbTag.tag_id).where(dbTag.tag_id.in_(new_servicio.tags))
    tags = db.scalars(query).all()
    for tag_id in tags:
        tag_servicio = dbTagServicio(tag_id=tag_id)
        servicio.tag_servicios.append(tag_servicio)
    db.add(servicio)
    db.commit()
    db.refresh(servicio)
    return servicio


@router.post("/{servicio_id}/tags", response_model=Servicio)
async def add_tag_to_servicio(
    tags: list[int],
    db: SessionLocal,
    servicio_id: int = Path(**servicio_id_metadata),
):
    """
    Retreive the tags associated with the Servicio.
    """
    query = select(dbServicio).where(dbServicio.servicio_id == servicio_id)
    servicio = db.scalars(query).first()
    for tag_id in tags:
        tag_servicio = dbTagServicio(tag_id=tag_id)
        servicio.tag_servicios.append(tag_servicio)
    db.add(servicio)
    db.commit()
    db.refresh(servicio)
    return servicio


@router.put("", response_model=dict[str, str])
async def bulk_update_servicios(
    servicios: List[ServicioUpdate], db: Session = Depends(get_db)
):
    """
    Perform bulk update of many servicios.
    """
    try:
        updated_servicios = [servicio.model_dump() for servicio in servicios]
        stmt = update(dbServicio).returning(dbServicio)
        servicios = db.scalars(stmt, updated_servicios)
        db.commit()
    except StaleDataError:
        raise HTTPException(status_code=404, detail="A servicio was not found")
    return {"message": "Bulk update successful"}


@router.delete("/{servicio_id}")
async def delete_servicio(
    servicio_id: int = Path(**servicio_id_metadata), db: Session = Depends(get_db)
):
    """
    Delete a specific Servicio.
    """
    transaction = (
        delete(dbServicio)
        .where(dbServicio.servicio_id == servicio_id)
        .returning(dbServicio.servicio_id)
    )
    deleted_servicio = db.execute(transaction).first()
    if deleted_servicio is None:
        raise HTTPException(
            status_code=404, detail=f"servicio id={servicio_id}was not found"
        )
    db.commit()
    return {"message": f"Servicio id={deleted_servicio[0]} deleted successfully"}


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
