FROM nginx:latest

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgeoip1 \
    geoip-database \
    nginx-module-geoip \
    && rm -rf /var/lib/apt/lists/*
