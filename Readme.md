# Warehouse Backend — Складской учет строительных материалов

Учебный backend-проект для предмета по базам данных / backend-разработке.  
Система реализует складской учет строительных материалов в строительной компании.

## 1. Функциональность

Реализованы основные сущности и операции:

- **Справочники**
  - `UNITS` — единицы измерения (шт, м, кг и т.п.)
  - `CATEGORIES` — категории материалов (иерархия: родитель → дочерние)
  - `MATERIALS` — материалы (артикул/sku, название, единица измерения, категория)
  - `SUPPLIERS` — поставщики (название, телефон, email, БИН/ИИН)
- **Номенклатура поставщиков**
  - `SUPPLIER_MATERIALS` — какие материалы может поставить поставщик, минимальная партия, срок поставки
  - `SUPPLIER_MATERIAL_PRICES` — история цен поставщиков по датам
- **Объекты и склады**
  - `PROJECTS` — строительные объекты/проекты
  - `WAREHOUSES` — склады на объектах
  - `WAREHOUSE_MATERIAL_POLICY` — минимальные остатки по складу×материалу
- **Закупки и движения склада**
  - `PURCHASE_ORDERS` + `PO_ITEMS` — заявки поставщикам и строки заявок
  - `STOCK_MOVEMENTS` — журнал приходов/выдач/перемещений/корректировок

Отчёты и аналитика (остатки, нехватки, доноры и т.п.) могут строиться на основе этих таблиц SQL-запросами.

---

## 2. Технологический стек

- **Язык:** Python 3.12
- **Web-фреймворк:** FastAPI
- **База данных:** PostgreSQL 16
- **ORM и миграции:** SQLAlchemy 2.x + Alembic
- **Контейнеризация:** Docker + docker compose
- **Документация API:** Swagger UI (`/docs`), OpenAPI 3.1

---

## 3. Структура проекта

```text
Project_Warehouse_backend/
├── app/
│   ├── main.py                   # Точка входа FastAPI
│   ├── db.py                     # Подключение к PostgreSQL (engine, SessionLocal, Base)
│   ├── models.py                 # SQLAlchemy-модели (таблицы по ER-диаграмме)
│   ├── schemas.py                # Pydantic-схемы (DTO) для API
│   ├── seed.py                   # Генератор тестовых данных (seed)
│   ├── requirements.txt          # Python-зависимости
│   ├── alembic.ini               # Конфигурация Alembic
│   └── alembic/
│       ├── env.py                # Настройки автогенерации миграций
│       ├── script.py.mako        # Шаблон для новых migration-файлов
│       └── versions/
│           └── 9be161fa8ad4_init_schema.py
│
├── Dockerfile                    # Docker-образ backend сервиса
├── docker-compose.yml            # Backend + PostgreSQL
├── .gitignore                    # Файлы, которые не должны попадать в репозиторий
└── README.md                     # Инструкция запуска + отчёт
```text
---

## 4. Запуск локально (без Docker)

Требуется установленный PostgreSQL или контейнер с PostgreSQL, проброшенный на localhost:15432.

Создать виртуальное окружение (по желанию) и установить зависимости:

```
pip install -r requirements.txt
```

Убедиться, что PostgreSQL доступен по адресу:

```
postgresql://warehouse_user:warehouse_password@localhost:15432/warehouse_db
```

(эти параметры заданы в app/db.py как значение по умолчанию).

Применить миграции Alembic:

```
cd app
alembic upgrade head
```

(Опционально) заполнить базу тестовыми данными:

```
python -m seed
```

Запустить приложение:

```
uvicorn main:app --reload
```

Проверка:

- http://127.0.0.1:8000/ping → {"status": "ok"}
- http://127.0.0.1:8000/docs → Swagger UI

---

## 5. Запуск через Docker / docker compose

Backend и база данных можно запустить одной командой.

Перейти в директорию app:

```
cd app
```

Собрать образ и запустить сервисы:

```
docker compose up --build
```

Будут подняты 2 сервиса:

- warehouse_db — PostgreSQL 16 (:5432, снаружи проброшен на localhost:15432)
- warehouse_backend — FastAPI-backend (:8000)

Проверка:

- http://127.0.0.1:8000/ping
- http://127.0.0.1:8000/docs

---

## 6. Миграции Alembic

Миграции настроены через alembic.ini и alembic/env.py, где подключена Base.metadata из models.py.

Основные команды (из каталога app):

Создать новую ревизию (если меняется модель):

```
alembic revision --autogenerate -m "comment"
```

Применить все миграции:

```
alembic upgrade head
```

Откатить на одну версию назад:

```
alembic downgrade -1
```

---

## 7. Заполнение БД тестовыми данными (seed)

Тестовые данные генерируются скриптом seed.py.

Команда (из каталога app):

```
python -m seed
```

Скрипт:

- очищает основные таблицы (TRUNCATE ... CASCADE)
- заполняет UNITS, CATEGORIES, SUPPLIERS, MATERIALS
- создает SUPPLIER_MATERIALS и SUPPLIER_MATERIAL_PRICES

После запуска можно проверить через:

- Swagger (GET /materials, GET /suppliers)
- SQL-клиент (например, DBeaver)

---

## 8. Тестирование API

Можно тестировать через Swagger или cURL.

Примеры cURL:

Проверка ping:

```
curl http://127.0.0.1:8000/ping
```

Список материалов:

```
curl http://127.0.0.1:8000/materials
```

Создание поставщика:

```
curl -X POST "http://127.0.0.1:8000/suppliers" ^
-H "Content-Type: application/json" ^
-d "{"name": "ТОО СтройПоставка", "phone": "+7 700 111 22 33"}"
```

---

## 9. Соответствие требованиям первой части

Реализовано:

- справочники материалов, поставщиков, единиц, категорий
- номенклатура поставщиков
- история цен
- объекты/склады
- политики минимальных остатков
- заявки поставщикам
- движения склада (приход/выдача)

Нефункциональные требования:

- DATABASE_URL через переменные окружения
- структурная архитектура (models / schemas / main)
- обработка ошибок HTTP 400 / 404
- Docker + docker compose
- PostgreSQL + Alembic миграции
- Автоматическая документация Swagger/OpenAPI

