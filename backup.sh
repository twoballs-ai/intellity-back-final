#!/bin/bash

# Настройки базы данных
export PGPASSWORD="gGHJDKSDK!UEssa09984!_KK"
PGUSER="postgres"
PGHOST="79.174.94.29"
PGDATABASE="courserio_db"
PGPORT=5432

# Путь и имя файла для сохранения дампа
BACKUP_PATH="backup"
FILENAME="${PGDATABASE}_backup_$(date +%Y%m%d).sql"

# Создание директории для бэкапа, если она не существует
if [ ! -d "$BACKUP_PATH" ]; then
  mkdir -p "$BACKUP_PATH"
fi

# Создание дампа базы данных
echo "Создание дампа базы данных..."
pg_dump -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -F p -d "$PGDATABASE" -f "$BACKUP_PATH/$FILENAME"

# Проверка успешности выполнения
if [ $? -eq 0 ]; then
  echo "Дамп базы данных успешно создан и сохранен в $BACKUP_PATH/$FILENAME"
else
  echo "Ошибка при создании дампа базы данных."
fi
