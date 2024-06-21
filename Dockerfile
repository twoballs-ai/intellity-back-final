# Stage 1: Build stage
FROM python:3.11-slim as builder

# Set environment variables
ENV POETRY_VERSION=1.8.2 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install Poetry
RUN pip install --no-cache-dir "poetry==$POETRY_VERSION"

# Create a directory for the application
WORKDIR /app

COPY pyproject.toml poetry.lock ./
# Install dependencies with Poetry
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

COPY . .

# Stage 2: Final stage
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
    
WORKDIR /app

# Copy the dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy the application code
COPY . .

# Expose the application port
EXPOSE 8000

# Update the command to include the necessary flags
CMD ["uvicorn", "intellity_back_final.main:app", "--host", "0.0.0.0", "--port", "8000", "--forwarded-allow-ips", "*", "--proxy-headers"]
