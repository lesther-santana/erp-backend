from pydantic import BaseModel, Field


class ErrorObject(BaseModel):
    status: int = Field(examples=[400])
    detail: str


class ServerError(BaseModel):
    status: int = Field(examples=[500])
    detail: str
