#!/bin/bash

echo "Запускаем проект..."

if [ "$(docker ps -q -f name=postgres-db)" = "" ]; then
  echo "Запускаем базу данных..."
  docker run -d --name postgres-db --network arxiv-net \
    -e POSTGRES_USER=arxiv_user \
    -e POSTGRES_PASSWORD=arxiv_pass \
    -e POSTGRES_DB=arxiv_db \
    -p 5432:5432 \
    postgres:16-alpine
fi

docker run -d --name arxiv-api --network arxiv-net -p 8000:8000 arxiv-api
echo "Приложение запущено на порту 8000"


docker run -d --name nginx-proxy --network arxiv-net -p 80:80 \
  -v "$(pwd)/nginx.conf:/etc/nginx/nginx.conf:ro" nginx:alpine
echo "Прокси запущен на порту 80"

echo "Всё готово!"
echo "Тест: http://127.0.0.1:80/parse?url=https://arxiv.org/list/cs/recent?skip=0&show=10"