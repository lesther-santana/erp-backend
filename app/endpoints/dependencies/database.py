from sqlalchemy.orm import Session
from fastapi import Depends
from typing import Annotated
from app.database import get_db

sessionDep = Annotated[Session, Depends(get_db)]
