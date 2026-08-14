#!/usr/bin/env bash
set -euo pipefail

echo "Asegurando que la base de datos esté arriba..."
docker compose up -d db

echo "Corriendo tests..."
uv run pytest
