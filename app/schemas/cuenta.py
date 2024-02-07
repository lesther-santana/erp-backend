from typing import List, TYPE_CHECKING

from pydantic import BaseModel, ConfigDict

from .common import CommonDateFields
from .servicio import Servicio


if TYPE_CHECKING:
    from .cliente_empresa import EmpresaInDB


class CuentaBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class CuentaNew(CuentaBase):
    rnc: str
    servicios: list[int]


class CuentaInDB(CuentaBase):
    cuenta_id: int
    rnc: str


class Cuenta(CuentaInDB, CommonDateFields):
    servicios: List["Servicio"]
    empresa: "EmpresaInDB"


class CuentaEmpresa(CuentaInDB):
    servicios: List["Servicio"]
