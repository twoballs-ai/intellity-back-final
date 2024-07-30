# env.py

from logging.config import fileConfig
import os
from dotenv import load_dotenv

from sqlalchemy import engine_from_config, pool
from alembic import context
from intellity_back_final.database import Base

# Import handlers to register event listeners
import intellity_back_final.handlers  # Ensure this is imported
load_dotenv()
# this is the Alembic Config object, which provides access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set the SQLAlchemy URL using the environment variable
config.set_main_option('sqlalchemy.url', os.getenv('SQLALCHEMY_DATABASE_URL'))

# Import your models for 'autogenerate' support
from intellity_back_final.models.course_editor_lms_models import *
from intellity_back_final.models.user_models import *
from intellity_back_final.models.course_study_lms_models import *
from intellity_back_final.models.blog_models import *
# Set the target metadata
target_metadata = [Base.metadata]

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL and not an Engine, though an Engine is acceptable here as well.
    Calls to context.execute() here emit the given string to the script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine and associate a connection with the context.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
