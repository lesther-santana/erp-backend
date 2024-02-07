from pydantic import BaseModel


class Empleado(BaseModel):
    nombre: str
