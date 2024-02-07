from pydantic import BaseModel, ConfigDict


class SecBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    pass


class BearerToken(SecBase):
    access_token: str
    expires_at: int
    token_type: str = "Bearer"


class AuthRequest(BaseModel):
    email: str
    password: str
