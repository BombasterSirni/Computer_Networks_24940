#!/bin/bash

echo "=== Запуск Arxiv Parser API ==="

# Очистка старых контейнеров приложения и прокси
echo "Очищаем старые контейнеры..."
docker rm -f arxiv-api nginx-proxy 2>/dev/null || true

# Создаём сеть
if [ "$(docker network ls -q -f name=arxiv-net)" = "" ]; then
    echo "Создаём сеть arxiv-net..."
    docker network create arxiv-net
else
    echo "Сеть arxiv-net уже существует"
fi

# Запускаем базу данных
if [ "$(docker ps -q -f name=postgres-db)" = "" ]; then
    echo "Запускаем PostgreSQL..."
    docker run -d \
      --name postgres-db \
      --network arxiv-net \
      -e POSTGRES_USER=arxiv_user \
      -e POSTGRES_PASSWORD=arxiv_pass \
      -e POSTGRES_DB=arxiv_db \
      -p 5432:5432 \
      postgres:16-alpine

    echo "Ожидаем запуска PostgreSQL..."
    sleep 5

    # Создаём таблицу
    echo "Создаём таблицу arxiv_articles..."
    docker exec -it postgres-db psql -U arxiv_user -d arxiv_db -c "
        CREATE TABLE IF NOT EXISTS arxiv_articles (
            id SERIAL PRIMARY KEY,
            arxiv_id TEXT UNIQUE NOT NULL,
            title TEXT,
            authors TEXT,
            subjects TEXT,
            url TEXT,
            parsed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        GRANT ALL PRIVILEGES ON TABLE arxiv_articles TO arxiv_user;
        GRANT USAGE, SELECT, UPDATE ON SEQUENCE arxiv_articles_id_seq TO arxiv_user;
    "
else
    echo "База данных уже работает"
fi

# Собираем образ
echo "Собираем образ arxiv-api..."
docker build --no-cache -t arxiv-api .

# Запускаем приложение
echo "Запускаем приложение (порт 8000)..."
docker run -d \
  --name arxiv-api \
  --network arxiv-net \
  -p 8000:8000 \
  arxiv-api

# Запускаем Nginx
echo "Запускаем Nginx-прокси (порт 80)..."
docker run -d \
  --name nginx-proxy \
  --network arxiv-net \
  -p 80:80 \
  -v "$(pwd)/nginx.conf:/etc/nginx/nginx.conf:ro" \
  nginx:latest

echo ""
echo "Проект успешно запущен!"
echo "Тест: http://127.0.0.1/parse?url=https://arxiv.org/list/cs/recent?skip=0&show=5"