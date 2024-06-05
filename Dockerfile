# Используем официальный образ Python для сборки
FROM python:3.11-slim

# Устанавливаем зависимости
WORKDIR /app

# Скопируем requirements.txt
COPY requirements.txt .

# Установим зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Скопируем исходный код приложения
COPY . .

# Установим команду запуска приложения
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]