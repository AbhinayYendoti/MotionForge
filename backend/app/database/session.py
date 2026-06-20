"""Database session factory with Neon PostgreSQL production tuning.

Connection pool settings are sized for a Render starter instance:
  • pool_size=5      — persistent connections kept alive
  • max_overflow=10  — burst capacity beyond pool_size
  • pool_recycle     — recycle connections before Neon's idle timeout (~5 min)
  • pool_pre_ping    — detect stale connections before handing them out
  • sslmode=require  — enforced for Neon (and any other TLS-only PG host)
"""
from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings


def _make_engine():
    db_url = settings.database_url

    # Build connect_args: always require SSL for hosted PostgreSQL.
    # If the user has already embedded sslmode in the URL we don't duplicate it,
    # but the connect_args version is honoured by psycopg regardless.
    connect_args: dict = {}
    is_postgres = db_url.startswith("postgresql") or db_url.startswith("postgres")
    if is_postgres and "sqlite" not in db_url:
        connect_args["sslmode"] = "require"
        # Force TCP keepalives to prevent PgBouncer/Neon from dropping idle connections
        # during long-running Remotion renders.
        connect_args["keepalives"] = 1
        connect_args["keepalives_idle"] = 30
        connect_args["keepalives_interval"] = 10
        connect_args["keepalives_count"] = 5

    engine_kwargs: dict = {
        "pool_pre_ping": True,
    }
    if is_postgres:
        engine_kwargs.update(
            {
                "pool_size": 5,
                "max_overflow": 10,
                "pool_timeout": 30,
                "pool_recycle": 1800,  # 30 min — well under Neon's idle cutoff
                "connect_args": connect_args,
            }
        )

    return create_engine(db_url, **engine_kwargs)


engine = _make_engine()
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
