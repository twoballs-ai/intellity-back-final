# Используем официальный образ Python в качестве базового
FROM python:3.11

# Устанавливаем curl и pyenv
RUN apt-get update && \
    apt-get install -y curl build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python-openssl git && \
    curl https://pyenv.run | bash

# Настройка окружения для pyenv
ENV PYENV_ROOT /root/.pyenv
ENV PATH $PYENV_ROOT/shims:$PYENV_ROOT/bin:$PATH

# Устанавливаем Python через pyenv
RUN pyenv install 3.11.0 && pyenv global 3.11.0

# Устанавливаем Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Добавляем Poetry в PATH
ENV PATH /root/.local/bin:$PATH

# Устанавливаем зависимости через Poetry
COPY pyproject.toml poetry.lock /app/
WORKDIR /app
RUN poetry install --no-root --no-dev

# Копируем весь проект в контейнер
COPY . /app

# Открываем порт для приложения
EXPOSE 8000

# Запускаем FastAPI сервер с использованием Uvicorn
CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]