from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import settings

# SQLite needs check_same_thread=False for FastAPI
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=settings.DEBUG,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _add_column_if_missing(conn, table: str, column: str, col_def: str) -> None:
    """SQLite-compatible column migration — adds column only when absent."""
    result = conn.execute(text(f"PRAGMA table_info({table})"))
    existing = {row[1] for row in result.fetchall()}
    if column not in existing:
        conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {col_def}"))


def init_db():
    """Create all tables and apply lightweight column migrations."""
    Base.metadata.create_all(bind=engine)

    if not settings.DATABASE_URL.startswith("sqlite"):
        return  # Postgres/MySQL handle migrations differently — use Alembic

    with engine.connect() as conn:
        # sites — Phase 2/3 columns
        _add_column_if_missing(conn, "sites", "hide_branding",          "BOOLEAN DEFAULT 0")
        _add_column_if_missing(conn, "sites", "monthly_query_limit",    "INTEGER DEFAULT 50")
        _add_column_if_missing(conn, "sites", "user_openai_key",        "VARCHAR")
        _add_column_if_missing(conn, "sites", "recrawl_interval_hours", "INTEGER DEFAULT 0")
        _add_column_if_missing(conn, "sites", "webhook_url",            "VARCHAR")
        _add_column_if_missing(conn, "sites", "ab_testing_enabled",     "BOOLEAN DEFAULT 0")
        # chat_messages — Phase 1/4 columns
        _add_column_if_missing(conn, "chat_messages", "was_answered",       "BOOLEAN DEFAULT 1")
        _add_column_if_missing(conn, "chat_messages", "confidence",         "VARCHAR DEFAULT 'high'")
        _add_column_if_missing(conn, "chat_messages", "sentiment",          "VARCHAR DEFAULT 'neutral'")
        _add_column_if_missing(conn, "chat_messages", "prompt_variant_id",  "VARCHAR")
        conn.commit()
