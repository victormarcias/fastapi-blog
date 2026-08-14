#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="fastapi-blog-504020"
REGION="us-east4"
SERVICE="fastapi-service"
IMAGE="us-east4-docker.pkg.dev/${PROJECT_ID}/fastapi-repo/fastapi-app"

RUN_POPULATE=false

for arg in "$@"; do
  case "$arg" in
    --populate) RUN_POPULATE=true ;;
    *)
      echo "Uso: $0 [--populate]"
      exit 1
      ;;
  esac
done

echo "Verificando estado del repo..."
if [ -n "$(git status --porcelain)" ]; then
  echo "Hay cambios sin commitear. Commiteá o descartá antes de deployar a prod."
  exit 1
fi

git fetch origin
if [ "$(git rev-parse @)" != "$(git rev-parse @{u})" ]; then
  echo "Tu rama local no está sincronizada con origin. Hacé git pull / git push antes de deployar."
  exit 1
fi

echo "Corriendo tests y buildeando la imagen en Cloud Build..."
gcloud builds submit --config cloudbuild.yaml --substitutions=_IMAGE="$IMAGE" --project "$PROJECT_ID"

echo "Leyendo DATABASE_URL de prod desde Cloud Run..."
PROD_DATABASE_URL=$(gcloud run services describe "$SERVICE" --region "$REGION" --project "$PROJECT_ID" --format=json \
  | python3 -c "import json,sys; d=json.load(sys.stdin); envs=d['spec']['template']['spec']['containers'][0]['env']; print(next(e['value'] for e in envs if e['name']=='DATABASE_URL'))")

echo "Aplicando migraciones contra Neon (prod)..."
DATABASE_URL="$PROD_DATABASE_URL" uv run alembic upgrade head

if [ "$RUN_POPULATE" = true ]; then
  echo "Poblando la base de datos de prod (Neon)..."
  DATABASE_URL="$PROD_DATABASE_URL" uv run python populate_db.py
fi

echo "Deployando a Cloud Run..."
gcloud run deploy "$SERVICE" --image "$IMAGE" --region "$REGION" --project "$PROJECT_ID"

echo ""
echo "Listo. App en producción:"
echo "  https://victormarcias.online/hero-blog"
