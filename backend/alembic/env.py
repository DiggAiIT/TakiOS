import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context
import sys
import os

# Ensure backend app is in path
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))

from app.config import settings
from app.database import Base

# Import all layer models so Base/AuditBase metadata knows about them
from app.core.auth.models import *
from app.layers.L01_level_selection.models import *
from app.layers.L02_tech_units.models import *
from app.layers.L03_subjects_modules.models import *
from app.layers.L04_content_eselsbruecken.models import *
from app.layers.L05_knowledge_assessment.models import *
from app.layers.L06_project_creation.models import *
from app.layers.L07_faculty_collaboration.models import *
from app.layers.L08_product_frontend.models import *
from app.layers.L09_dimensional_realization.models import *
from app.layers.L10_io_definition.models import *
from app.layers.L11_legal_compliance.models import *
from app.layers.L12_quality_management.models import *
from app.layers.L13_social_engineering_impact.models import *
# access to the values within the .ini file in use.
config = context.config

# Dynamically set the sqlalchemy.url from our settings
config.set_main_option("sqlalchemy.url", settings.database_url)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
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

async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
