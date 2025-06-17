from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os
import sys

# Pfad zur App setzen
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "app"))

from app import models  # Importiere alle Models, die gemappt werden sollen
from app.config import settings  # Deine eigene Konfigurationslogik

# Diese Config-Objekt wird von alembic.ini gelesen
config = context.config

# Logging konfigurieren (optional)
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Ziel-Metadaten (für Autogenerate)
target_metadata = models.Base.metadata

# SQLAlchemy-URL aus deiner Konfiguration
config.set_main_option("sqlalchemy.url", settings.database_url)

def run_migrations_offline():
    """Migrations im Offline-Modus (nur SQL-Generierung)"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Migrations im Online-Modus (direkt auf DB anwenden)"""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
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


# Entscheidung, ob offline oder online Modus
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
