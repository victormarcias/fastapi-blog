# hero-blog

A blog API + server-rendered frontend built with FastAPI, deployed on Google Cloud Run with Neon (Postgres) as the database.

Live at: https://victormarcias.online/hero-blog

## Features

- **Auth**: JWT-based registration/login, password reset via email (Mailtrap), password change
- **Posts**: CRUD with pagination
- **Users**: public profiles, per-user paginated post lists, profile picture upload (Amazon S3)
- **Frontend**: server-rendered pages (Jinja2 + Bootstrap) for home, login, register, account, posts
- **API docs**: Swagger UI (`/hero-blog/docs`) and ReDoc (`/hero-blog/redoc`)
- **Health check**: `/status` verifies DB connectivity
- **Security**: security headers middleware (HSTS, X-Frame-Options, etc.), Argon2 password hashing
- Dockerized with a multi-stage build, running as a non-root user
- Separate environments: local Postgres for dev, [Neon](https://neon.tech) for prod
- Automated test suite (pytest) that runs in Cloud Build before every deploy

## How to run

### Prerequisites

- [Docker](https://www.docker.com/) — installed and **running** (Docker Desktop must be open), only for local dev/tests
- [uv](https://docs.astral.sh/uv/) — runs Alembic locally, and tests when run outside Cloud Build
- `gcloud` CLI, authenticated — only needed to deploy to production (no Docker required — tests and the image build run in Cloud Build)

### Local development

```bash
./run-project-dev.sh              # build, start containers, run migrations
./run-project-dev.sh --test        # ...and run the test suite
./run-project-dev.sh --populate    # ...and seed the DB with demo data
./run-project-dev.sh --test --populate
```

App runs at `http://localhost:8000/hero-blog`, docs at `http://localhost:8000/hero-blog/docs`.

Uses a local Postgres container (`bloguser`/`blogpass`) — no external dependencies needed.

### Tests only

```bash
./run-tests.sh
```

Runs against an isolated local `test_blog` database.

### Deploy to production

```bash
./run-project-prod.sh              # test, build, migrate Neon, deploy to Cloud Run
./run-project-prod.sh --populate   # ...and seed prod with demo data
```

Requires a clean working tree in sync with `origin/main`, and the `gcloud` CLI authenticated. Runs tests and builds the image in Cloud Build (`cloudbuild.yaml`, own ephemeral Postgres — no local Docker needed), pushes it to Artifact Registry, runs migrations against the production Neon database, then deploys to Cloud Run.
