from sqlalchemy import URL
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os


def build_db_engine():
    """
    Create an SQLAlchemy engine instance using configuration from environment variables
    """
    db_url = URL.create(
        drivername=os.environ["DB_DRIVER"],
        username=os.environ["DB_USERNAME"],
        password=os.environ["DB_PASSWORD"],
        host=os.environ["DB_HOST"],
        port=os.environ["DB_PORT"],
        database=os.environ["DB_NAME"],
    )
    engine = create_engine(db_url, pool_pre_ping=True)
    return engine


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


engine = build_db_engine()
SessionLocal = sessionmaker(bind=engine)
