#!/bin/bash

echo "Останавливаем контейнеры..."

docker stop arxiv-api nginx-proxy 2>/dev/null || true
docker rm arxiv-api nginx-proxy 2>/dev/null || true

echo "Контейнеры остановлены и удалены"
echo "База данных (postgres-db) осталась работать"