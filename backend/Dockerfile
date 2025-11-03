FROM python:3.11

WORKDIR /app

# Создаем папку для данных SQLite
RUN mkdir -p /app/data

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Создаем базу данных и применяем миграции
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]