"""Database selector - only uses real PostgreSQL database."""

import os


def _use_app_resource_db() -> bool:
    """Lakebase attached as an App database resource (injects PG*)."""
    return bool(os.getenv("PGHOST") and os.getenv("PGUSER"))


def _use_legacy_password_db() -> bool:
    return all([os.getenv("DB_HOST"), os.getenv("DB_USER"), os.getenv("DB_PASSWORD")])


if _use_app_resource_db():
    missing = [k for k in ("DATABRICKS_HOST", "DATABRICKS_CLIENT_ID", "DATABRICKS_CLIENT_SECRET") if not os.getenv(k)]
    if missing:
        raise ValueError(
            "Lakebase App database resource detected (PGHOST, PGUSER) but missing: "
            f"{missing}. These are required to mint an OAuth token for Postgres."
        )
elif not _use_legacy_password_db():
    raise ValueError(
        "PostgreSQL is required: either set PGHOST+PGUSER (App Lakebase resource) with "
        "DATABRICKS_HOST, DATABRICKS_CLIENT_ID, DATABRICKS_CLIENT_SECRET, or set "
        "DB_HOST, DB_USER, DB_PASSWORD for local/password access."
    )

# Only use real PostgreSQL database - no fallback
from .postgres_database import db

print("Using Lakebase PostgreSQL database")

__all__ = ['db']