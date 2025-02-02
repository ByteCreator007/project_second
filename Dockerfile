FROM python:3.10-slim

ENV PIP_DEFAULT_TIMEOUT=120

RUN pip install poetry

WORKDIR /app

COPY pyproject.toml poetry.lock* /app/

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root --with dev

COPY src/ /app/src/
COPY templates/ /app/templates/
COPY tests/ /app/tests/
COPY README.md /app/
COPY create_tables.py /app/
COPY seed_package_types.py /app/

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
