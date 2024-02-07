from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session
from ...database import get_db
from ...schemas import errors

session = Annotated[Session, Depends(get_db)]

errorResponses = {
    401: {
        "model": errors.ErrorObject,
        "description": "Unauthorized - The request requires user authentication.",
    },
    403: {
        "model": errors.ErrorObject,
        "description": "Forbidden - The server understood the request, but is refusing to fulfill it.",
    },
    404: {
        "model": errors.ErrorObject,
        "description": "Not Found - The requested resource could not be found.",
    },
    429: {
        "model": errors.ErrorObject,
        "description": "Too Many Requests - Rate limiting has been applied.",
    },
    500: {
        "model": errors.ServerError,
        "description": "Internal Server Error.",
    },
}
