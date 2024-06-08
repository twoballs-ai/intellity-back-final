FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1 \
    PYTHONUNBUFFERED 1

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r /intellity_back_final/requirements.txt

COPY . .
# Копируем файл окружения
# COPY .env .env

EXPOSE 8000

CMD ["uvicorn", "intellity_back_final.main:app", "--host", "0.0.0.0", "--port", "8000"]

# FROM python:3.11 as requirements-stage

# WORKDIR /tmp

# # не изменять
# RUN pip install poetry

# COPY ./pyproject.toml ./poetry.lock* /tmp/

# RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

# FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11

# COPY --from=requirements-stage /tmp/requirements.txt /intellity_back_final/requirements.txt

# RUN pip install --no-cache-dir --upgrade -r /intellity_back_final/requirements.txt

# COPY ./intellity_back_final /intellity_back_final