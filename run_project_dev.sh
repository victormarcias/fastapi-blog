#!/usr/bin/env bash
set -euo pipefail

RUN_TESTS=false
RUN_POPULATE=false

for arg in "$@"; do
  case "$arg" in
    --test) RUN_TESTS=true ;;
    --populate) RUN_POPULATE=true ;;
    *)
      echo "Uso: $0 [--test] [--populate]"
      exit 1
      ;;
  esac
done

echo "Levantando la app (Docker)..."
docker compose up -d --build

echo "Aplicando migraciones..."
docker compose exec -T app alembic upgrade head

if [ "$RUN_TESTS" = true ]; then
  ./run_tests.sh
fi

if [ "$RUN_POPULATE" = true ]; then
  echo "Poblando la base de datos..."
  docker compose exec -T app python populate_db.py
fi

echo ""
echo "Listo. API corriendo en:"
echo "  http://localhost:8000/hero-blog"
echo "  Docs (Swagger): http://localhost:8000/hero-blog/docs"
