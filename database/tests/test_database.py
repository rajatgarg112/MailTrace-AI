import pytest
from sqlalchemy import text
from app.core.config import settings
from app.core.database import Base, engine, get_db, SessionLocal


def test_database_url_configuration():
    assert settings.DATABASE_URL is not None
    assert "sqlite" in settings.DATABASE_URL.lower()


def test_database_engine_connection():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        scalar = result.scalar()
        assert scalar == 1


def test_get_db_session_generator():
    db_gen = get_db()
    session = next(db_gen)
    assert session is not None
    try:
        result = session.execute(text("SELECT 1")).scalar()
        assert result == 1
    finally:
        with pytest.raises(StopIteration):
            next(db_gen)


def test_base_orm_metadata(db_session):
    assert Base.metadata is not None
    Base.metadata.create_all(bind=db_session.get_bind())
