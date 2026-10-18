FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DATABASE_URL=sqlite+aiosqlite:////data/formetr.db

WORKDIR /app

COPY requirements.txt pyproject.toml setup.cfg alembic.ini ./
COPY app ./app
COPY alembic ./alembic

RUN pip install --no-cache-dir -e .

RUN mkdir -p /data
VOLUME ["/data"]

CMD ["sh", "-c", "alembic upgrade head && python -m app"]
