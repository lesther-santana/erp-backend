import pytest
from typing import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models, main, database

SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def db() -> Generator:
    models.Base.metadata.create_all(bind=engine)
    with TestingSessionLocal() as session:
        yield session


@pytest.fixture(scope="module")
def api_client(db) -> Generator:
    app = main.app
    app.dependency_overrides[database.get_db] = lambda: db
    with TestClient(app) as client:
        yield client
