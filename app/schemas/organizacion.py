import enum
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID


class OrganizacionBase(BaseModel):
    model_config = ConfigDict(use_enum_values=True)


class OrganizacionCreate(OrganizacionBase):
    nombre: str


class Organizacion(OrganizacionBase):
    organizacion_id: UUID
    nombre: str
    created_at: datetime


class UserRole(str, enum.Enum):
    SUPERUSER: str = "superuser"
    SUPERVISOR: str = "supervisor"
    COLLABORATOR: str = "collaborator"


class Empleado(OrganizacionBase):
    nombre: str
    email: str
    password: str
    rol: UserRole
