import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# Alembic Config object
config = context.config

# Логирование
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ---- ВАЖНО: добавляем корень проекта в sys.path ----
# На хосте:   .../Project_Warehouse_backend/app
# В контейнере: /code
project_root = os.path.dirname(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.append(project_root)

# Тут уже можно спокойно импортировать models
from models import Base

# Метаданные для автогенерации миграций
target_metadata = Base.metadata


def get_url() -> str:
    """
    Берём URL к БД:
    - сначала из переменной окружения DATABASE_URL (для Docker),
    - если её нет — из alembic.ini (для локального запуска).
    """
    env_url = os.getenv("DATABASE_URL")
    if env_url:
        return env_url
    return config.get_main_option("sqlalchemy.url")


def run_migrations_offline() -> None:
    """
    Миграции в 'offline' режиме.
    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Миграции в 'online' режиме.
    """
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = get_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
