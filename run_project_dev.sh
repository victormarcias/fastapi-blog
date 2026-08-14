#!/usr/bin/env bash
set -euo pipefail

echo "Levantando la app (Docker)..."
docker compose up -d --build

echo "Aplicando migraciones..."
docker compose exec -T app alembic upgrade head

./run_tests.sh

echo "Poblando la base de datos..."
docker compose exec -T app python populate_db.py

echo ""
echo "Listo. API corriendo en:"
echo "  http://localhost:8000/fastapi-blog"
echo "  Docs (Swagger): http://localhost:8000/docs"
