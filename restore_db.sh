#!/bin/bash

# Настройки базы данных
export PGPASSWORD="gGHJDKSDK!UEssa09984!_KK"
PGUSER="postgres"
PGHOST="79.174.94.29"
PGDATABASE="courserio_db"
PGPORT=5432

# Путь к файлу бэкапа
BACKUP_FILE="backup/courserio_db_backup_20240822.sql"

# Проверка существования файла
if [ ! -f "$BACKUP_FILE" ]; then
  echo "Файл бэкапа $BACKUP_FILE не найден!"
  exit 1
fi

# Удаление и создание базы данных
echo "Пересоздание базы данных $PGDATABASE..."
psql -h "$PGHOST" -U "$PGUSER" -c "DROP DATABASE IF EXISTS $PGDATABASE;"
psql -h "$PGHOST" -U "$PGUSER" -c "CREATE DATABASE $PGDATABASE;"

# Восстановление базы данных из дампа
echo "Восстановление базы данных из $BACKUP_FILE..."
psql -h "$PGHOST" -U "$PGUSER" -d "$PGDATABASE" -f "$BACKUP_FILE"

# Проверка успешности выполнения
if [ $? -eq 0 ]; then
  echo "База данных успешно восстановлена из $BACKUP_FILE"
else
  echo "Ошибка при восстановлении базы данных."
fi
