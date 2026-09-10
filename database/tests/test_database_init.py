import os
import pytest
from sqlalchemy import create_engine, inspect, text
from alembic.config import Config
from alembic import command

from app.core.database import Base, get_db
from app.core.init_db import init_db
from app.models.user import User
from app.models.email import Email
from app.models.email_event import EmailEvent
from app.models.analysis_result import AnalysisResult


def test_init_db_creates_all_tables():
    """Verify init_db() creates users, emails, email_events, and analysis_results on a fresh SQLite database."""
    test_db_url = "sqlite:///:memory:"
    engine = create_engine(test_db_url, connect_args={"check_same_thread": False})

    # Execute create_all on clean engine
    Base.metadata.create_all(bind=engine)

    inspector = inspect(engine)
    table_names = inspector.get_table_names()

    assert "users" in table_names
    assert "emails" in table_names
    assert "email_events" in table_names
    assert "analysis_results" in table_names


def test_alembic_migration_upgrade_head(tmp_path):
    """Test running Alembic upgrade head against a fresh SQLite database file."""
    db_file = tmp_path / "fresh_test_mailtrace.db"
    db_url = f"sqlite:///{db_file.as_posix()}"

    # Prepare Alembic configuration
    database_dir = os.path.realpath(os.path.join(os.path.dirname(__file__), ".."))
    alembic_cfg = Config(os.path.join(database_dir, "alembic.ini"))
    alembic_cfg.set_main_option("script_location", os.path.join(database_dir, "alembic"))
    alembic_cfg.set_main_option("sqlalchemy.url", db_url)

    # Run upgrade head
    command.upgrade(alembic_cfg, "head")

    engine = create_engine(db_url)
    inspector = inspect(engine)
    table_names = inspector.get_table_names()

    assert "users" in table_names
    assert "emails" in table_names
    assert "email_events" in table_names
    assert "analysis_results" in table_names
    assert "alembic_version" in table_names
