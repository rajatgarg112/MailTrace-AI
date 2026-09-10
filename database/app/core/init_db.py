import os
import sys

# Ensure database directory is in sys.path when executed directly as CLI script
database_dir = os.path.realpath(os.path.join(os.path.dirname(__file__), "..", ".."))
if database_dir not in sys.path:
    sys.path.insert(0, database_dir)

from app.core.database import engine, Base
import app.models  # noqa: F401


def init_db() -> None:
    """
    Creates all database tables defined in Base ORM models (users, emails, email_events, analysis_results).
    Safe to run repeatedly; will not overwrite or destroy existing tables.
    """
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
    print("Database tables initialized successfully!")
