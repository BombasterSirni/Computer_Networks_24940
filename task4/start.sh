#!/bin/bash

echo "=== Запуск Arxiv Parser API ==="

# 1. Создаём сеть, если её ещё нет
if [ "$(docker network ls -q -f name=arxiv-net)" = "" ]; then
    echo "Создаём сеть arxiv-net..."
    docker network create arxiv-net
else
    echo "Сеть arxiv-net уже существует"
fi

# 2. Запускаем базу данных
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
else
    echo "База данных уже работает"
fi

# 3. Собираем образ приложения
echo "Собираем образ arxiv-api..."
docker build -t arxiv-api .

# 4. Запускаем приложение
if [ "$(docker ps -q -f name=arxiv-api)" = "" ]; then
    echo "Запускаем приложение (порт 8000)..."
    docker run -d \
      --name arxiv-api \
      --network arxiv-net \
      -p 8000:8000 \
      arxiv-api
else
    echo "Приложение уже работает"
fi

# 5. Запускаем Nginx-прокси
if [ "$(docker ps -q -f name=nginx-proxy)" = "" ]; then
    echo "Запускаем Nginx-прокси (порт 80)..."
    docker run -d \
      --name nginx-proxy \
      --network arxiv-net \
      -p 80:80 \
      -v "$(pwd)/nginx.conf:/etc/nginx/nginx.conf:ro" \
      nginx:alpine
else
    echo "Nginx-прокси уже работает"
fi

echo ""
echo "Проект успешно запущен!"
echo "Тест: http://127.0.0.1/parse?url=https://arxiv.org/list/cs/recent?skip=0&show=5"
echo ""