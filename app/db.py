# app/db.py

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Для Docker контейнера значение придёт из переменной окружения DATABASE_URL
# Для локальной разработки используем дефолт на localhost:15432
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://warehouse_user:warehouse_password@localhost:15432/warehouse_db",
)

engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
