import enum
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID


class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    pass


class UserRole(str, enum.Enum):
    SUPERUSER: str = "superuser"
    SUPERVISOR: str = "supervisor"
    COLLABORATOR: str = "collaborator"


class UserCreate(UserBase):
    nombre: str
    email: str
    password: str
    rol: UserRole


class User(UserBase):
    usuario_id: UUID
    nombre: str
    email: str
    rol: UserRole
    created_at: datetime
