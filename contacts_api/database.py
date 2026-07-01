import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

if os.environ.get("TESTING") == "True":
    SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
else:
    SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://postgres:postgres123@localhost:5432/contacts_db"
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """
    Provides a transactional database session for FastAPI dependencies.
    Yields a SQLAlchemy Session object and closes it after the request completes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()