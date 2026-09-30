from pathlib import Path
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from backend.core.config import settings

class Base(DeclarativeBase):
    pass

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def init_db() -> None:
    from backend.database import models
    alembic_config = Config(str(Path(__file__).resolve().parents[2] / "alembic.ini"))
    alembic_config.set_main_option("script_location", str(Path(__file__).resolve().parents[2] / "alembic"))
    command.upgrade(alembic_config, "head")
    Base.metadata.create_all(bind=engine)
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    columns = {column["name"] for column in inspector.get_columns("mission_tasks")} if "mission_tasks" in tables else set()
    with engine.begin() as conn:
        if "retry_count" not in columns:
            conn.execute(text("ALTER TABLE mission_tasks ADD COLUMN retry_count INTEGER DEFAULT 0"))
        if "max_retries" not in columns:
            conn.execute(text("ALTER TABLE mission_tasks ADD COLUMN max_retries INTEGER DEFAULT 1"))
        agent_columns = {column["name"] for column in inspector.get_columns("agent_definitions")} if "agent_definitions" in tables else set()
        if "lifecycle_status" not in agent_columns and "agent_definitions" in tables:
            conn.execute(text("ALTER TABLE agent_definitions ADD COLUMN lifecycle_status VARCHAR(30) DEFAULT 'ACTIVE'"))
        if "retired_at" not in agent_columns and "agent_definitions" in tables:
            conn.execute(text("ALTER TABLE agent_definitions ADD COLUMN retired_at DATETIME"))

def check_db() -> bool:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
