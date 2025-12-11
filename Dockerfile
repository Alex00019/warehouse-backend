# Базовый образ с Python
FROM python:3.12-slim

# Рабочая директория внутри контейнера
WORKDIR /code

# Немного настроек Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# (опционально) инструменты для сборки зависимостей
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# Сначала копируем список зависимостей и ставим их
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Потом копируем код приложения из папки app
COPY app/ .

# Порт приложения
EXPOSE 8000

# Команда запуска backend-а
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
