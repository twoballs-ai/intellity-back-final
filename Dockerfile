# Используем официальный образ Python
FROM python:3.11

# Устанавливаем Poetry
RUN pip install poetry

# Устанавливаем переменную окружения для вывода сообщений
ENV PYTHONUNBUFFERED=1

# Создаем и устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы pyproject.toml и poetry.lock
COPY pyproject.toml poetry.lock ./

# Устанавливаем зависимости с помощью Poetry
RUN poetry install --no-root --no-dev

# Копируем остальные файлы приложения
COPY . .

# Открываем порт
EXPOSE 8000

# Команда для запуска приложения
CMD ["uvicorn", "intellity_back_final.main:app", "--host", "0.0.0.0", "--port", "8000"]