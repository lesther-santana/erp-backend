from typing import Optional
from enum import Enum

from pydantic import BaseModel, field_serializer, ConfigDict

from .cuenta import CuentaEmpresa
from .common import CommonDateFields


class PersonaEnum(Enum):
    fisica = "fisica"
    juridica = "juridica"


class ClienteBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ClienteCreate(ClienteBase):
    nombre: str
    telefono: str
    email: str


class ClienteUpdate(ClienteBase):
    telefono: Optional[str] = None
    email: Optional[str] = None


class ClienteInDB(ClienteCreate, CommonDateFields):
    cliente_id: int


class EmpresaBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    @field_serializer("tipo_de_persona", check_fields=False)
    def serialze_tipo_persona(self, tipo: PersonaEnum):
        return tipo.value


class EmpresaCreate(EmpresaBase):
    rnc: str
    nombre: str
    tipo_de_persona: PersonaEnum
    relacionados: list[int] = []


class EmpresaUpdate(EmpresaBase):
    nombre: Optional[str] = None
    tipo_de_persona: Optional[str] = None


class EmpresaInDB(EmpresaBase):
    rnc: str
    nombre: str
    tipo_de_persona: PersonaEnum


# Returned by empresas endpoint
class Empresa(EmpresaInDB):
    relacionados: Optional[list[ClienteInDB]] = []
    cuenta: Optional[CuentaEmpresa] = None


# Returned by clientes endpoint
class Cliente(ClienteBase, CommonDateFields):
    cliente_id: int
    empresas: list[Empresa] = []
