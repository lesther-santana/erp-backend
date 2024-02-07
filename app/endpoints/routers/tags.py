from fastapi import APIRouter, HTTPException, Depends, Path
from sqlalchemy import select, update, delete, insert
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import StaleDataError
from typing import List, Any, Annotated

from ..dependencies.common import errorResponses
from ..dependencies import auth
from ...models import Tag as dbTag
from ...database import get_db
from ...schemas.servicio import Tag, TagCreate, TagUpdate
from ...schemas.pagination import PagintationParams, PaginatedResponse


router = APIRouter(responses=errorResponses, dependencies=[Depends(auth.get_user)])
pagintationParams = Annotated[PagintationParams, Depends()]
SessionLocal = Annotated[Session, Depends(get_db)]
tag_id_metadata = {
    "title": "Tag id",
    "description": "The unique identifier for the Tag.",
}


@router.get("/{tag_id}", response_model=Tag)
async def get_tag(tag_id: int = Path(**tag_id_metadata), db: Session = Depends(get_db)):
    """
    Retrieve information about a specific Tag.
    """
    query = select(dbTag).where(dbTag.tag_id == tag_id)
    tag = db.scalars(query).first()
    if tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


@router.get("", response_model=PaginatedResponse[Tag])
async def get_multiple_tags(params: pagintationParams, db: SessionLocal):
    """
    Retrieve a multiple tags with pagination.
    """
    query = select(dbTag).offset(params.offset).limit(params.limit)
    tags = db.scalars(query).all()
    response = paginate(params, tags)
    return response


@router.post("")
async def bulk_create_tags(new_tags: List[TagCreate], db: SessionLocal):
    """
    Create one or multiple tags.
    """
    new_tags = [t.model_dump() for t in new_tags]
    stmt = insert(dbTag).returning(dbTag)
    tags = db.scalars(stmt, new_tags)
    db.commit()
    return tags


@router.put("")
async def bulk_update_tags(tags: List[TagUpdate], db: Session = Depends(get_db)):
    """
    Update multiple Tags.
    """
    try:
        updated_tags = [tag.model_dump() for tag in tags]
        db.execute(update(dbTag), updated_tags)
        db.commit()
    except StaleDataError:
        raise HTTPException(status_code=404, detail="A Tag was not found")
    return {"message": "Bulk update successful"}


@router.delete("/{tag_id}")
async def delete_tag(
    tag_id: int = Path(**tag_id_metadata), db: Session = Depends(get_db)
):
    """
    Delete a specific Tag.
    """
    stmt = delete(dbTag).where(dbTag.tag_id == tag_id).returning(dbTag.tag_id)
    deleted_tag = db.scalars(stmt).first()
    if deleted_tag is None:
        raise HTTPException(status_code=404, detail=f"Tag id={tag_id} not found")
    db.commit()
    return {"message": f"Servicio id={deleted_tag} deleted successfully"}


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
