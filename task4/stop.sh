#!/bin/bash

# 1. Останавливаем и удаляем контейнеры приложения и прокси
echo "Останавливаем и удаляем arxiv-api и nginx-proxy..."
docker stop arxiv-api nginx-proxy 2>/dev/null || true
docker rm arxiv-api nginx-proxy 2>/dev/null || true

echo ""
echo "Готово."
echo "Порты 80 и 8000 свободны"
echo "База данных жива на localhost:5432"
echo "Для полного удаления базы: docker rm -f postgres-db"