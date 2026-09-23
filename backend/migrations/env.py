"""Alembic environment — wired to the app's async engine, settings-driven
DB URL, and ORM metadata so `alembic revision --autogenerate` works out of
the box. See architecture doc Section 5.3."""

import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

from app.core.config import settings
from app.core.database import Base

# Import every module's models here so they register on Base.metadata
# and are picked up by autogenerate.
from app.modules.auth import models as auth_models  # noqa: F401
from app.modules.masters import models as masters_models  # noqa: F401
from app.modules.sap_outward import models as sap_outward_models  # noqa: F401
from app.modules.dc_verification import models as dc_verification_models  # noqa: F401
from app.modules.deviations import models as deviations_models  # noqa: F401
from app.modules.sap_processing import models as sap_processing_models  # noqa: F401
from app.modules.ppc_collection import models as ppc_collection_models  # noqa: F401
from app.modules.qa_inspection import models as qa_inspection_models  # noqa: F401
from app.modules.zqmtl1 import models as zqmtl1_models  # noqa: F401
from app.modules.storage import models as storage_models  # noqa: F401

config = context.config
config.set_main_option("sqlalchemy.url", settings.database_url.replace("%", "%%"))


if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
