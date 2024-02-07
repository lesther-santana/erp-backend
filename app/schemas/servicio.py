from pydantic import BaseModel, ConfigDict
from typing import Optional
from .common import CommonDateFields


class ServicioBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    nombre: str


class ServicioCreate(ServicioBase):
    tags: list[int] = []


# Properties shared by models stored in DB
class ServicioInDB(ServicioBase):
    servicio_id: int
    nombre: str


class ServicioUpdate(ServicioInDB):
    pass


class TagBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    nombre: Optional[str] = None


class TagCreate(TagBase):
    nombre: str


class TagUpdate(TagBase):
    pass


# Properties shared by models stored in DB
class TagInDB(TagBase):
    tag_id: int
    nombre: str


# Return via API
class Tag(TagInDB, CommonDateFields):
    pass
    servicios: list[ServicioInDB]


# Return via API
class Servicio(ServicioInDB):
    pass
    tags: list[TagInDB]
