# INSP Dahej

Internal web app for the Inspection Department at Dahej. Tracks day-to-day inspection **jobs** across plants and logs **overtime** for staff. Built on a Django + Vue stack and deployed via Docker.

## What it does

- **Jobs** — record inspection work performed by a user on a given date: job type, plant, count, done/pending status, remarks, and optional file attachments (photos, reports).
- **Overtime** — log per-user overtime hours by date, with the plants the OT was worked against and remarks.
- **Masters** — manage the lookup lists used by jobs and overtime: **Job Types** and **Plants**.
- **Auth** — login/register backed by Django users and Knox tokens; every create/update is audited with `created_by` / `updated_by` and an updation remark.

## Stack

| Layer | Tech |
|---|---|
| Backend | Django 6, DRF, django-rest-knox (token auth), psycopg 3, gunicorn, whitenoise |
| Database | PostgreSQL 16 |
| Frontend | Vue 3, Vite, Vue Router, Pinia, axios, Vuetify 3 (iOS-inspired glassmorphism theme) |
| Prod server | Nginx 1.27 (alpine) |
| Containers | Docker / Docker Compose |
| Backend base image | Ubuntu 24.04 |

Knox tokens stored in browser `localStorage`. Uploaded job files are served from `/media/`.

## Project layout

```
insp_dahej/
├── backend/
│   ├── core/             # Django project (settings.py, urls.py, ...)
│   ├── accounts/         # auth app (register/login/logout/me)
│   ├── dahej_insp/       # domain app: JobType, Plant, Job, JobFile, OverTime
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── requirements.txt
│   └── start.sh / stop.sh
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   ├── client.js          # axios + token interceptor
│   │   │   └── dahej.js           # jobs / overtime / job-types / plants endpoints
│   │   ├── stores/auth.js
│   │   ├── router/index.js
│   │   ├── plugins/vuetify.js
│   │   └── views/
│   │       ├── LoginView.vue / RegisterView.vue / ProfileView.vue
│   │       └── dahej/
│   │           ├── JobsView.vue
│   │           ├── OverTimesView.vue
│   │           ├── JobTypesView.vue
│   │           └── PlantsView.vue
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── start.sh / stop.sh
└── nginx/                # prod-like (port 80, nginx + gunicorn + db)
    ├── Dockerfile        # multi-stage: builds frontend + nginx image
    ├── nginx.conf
    ├── docker-compose.yml
    └── start.sh / stop.sh
```

## Domain model

Defined in [backend/dahej_insp/models.py](backend/dahej_insp/models.py):

- **JobType** — `name` (unique). E.g. "Visual Inspection", "Thickness Survey".
- **Plant** — `name` (unique). The plant the work was carried out at.
- **Job** — `performer` (User), `job_type`, `plant`, `job_date`, `count`, `done`, `remarks`, audit fields.
- **JobFile** — file attachment(s) tied to a `Job`, uploaded to `media/job_files/`.
- **OverTime** — `user`, `plants` (M2M), `date`, `hours` (decimal), `remarks`, audit fields.

All write-side records carry `created_at` / `created_by` / `updated_at` / `updated_by` / `updation_remarks` for traceability.

## Prerequisites

- **Docker Desktop** (with Docker Compose v2)
- **Git Bash** or **WSL** on Windows (for running `*.sh` scripts)
- **Node.js 20+** *(only if running Vite directly on host)*
- **Python 3.12+** *(only for one-off `manage.py` commands outside Docker)*

## First-time setup

```bash
git clone <your-repo-url> insp_dahej
cd insp_dahej

# Backend env
cp backend/.env.example backend/.env
python -c "import secrets; print(secrets.token_urlsafe(50))"
# Paste into DJANGO_SECRET_KEY in backend/.env

# Frontend env
cp frontend/.env.example frontend/.env

# (Optional) prod-like stack
cp nginx/.env.example nginx/.env
python -c "import secrets; print(secrets.token_urlsafe(50))"
# Paste into DJANGO_SECRET_KEY in nginx/.env
```

## Running — development

Two stacks, two terminals.

```bash
# Terminal 1: backend + db
cd backend
./start.sh
# http://localhost:8000/api/health/
# http://localhost:8000/admin/

# Terminal 2: frontend
cd frontend
./start.sh
# http://localhost:5173/
```

`start.sh` runs `docker compose up --build`, applies migrations, and creates the superuser from `DJANGO_SUPERUSER_*` if missing.

To stop:

```bash
./stop.sh           # preserves data
./stop.sh --wipe    # destroys postgres volume AND uploaded media
```

## Running — production-like (local)

Stop the dev stacks first to free Postgres' port. Then:

```bash
cd nginx
./start.sh
```

This builds a single self-contained stack:

- **db** — Postgres (separate volume from dev)
- **web** — Django via gunicorn (no source mount; baked into image)
- **nginx** — serves built Vue SPA + reverse-proxies `/api/`, `/admin/`, `/static/`, `/media/` to gunicorn

Access:

- App: http://localhost/
- API: http://localhost/api/health/
- Admin: http://localhost/admin/

## Environment files

Each stack has its own `.env` (gitignored) and `.env.example` (committed).

| Var | Used by | Notes |
|---|---|---|
| `DJANGO_SECRET_KEY` | backend, nginx | Distinct per env |
| `DJANGO_DEBUG` | backend, nginx | `True` in dev, `False` in prod |
| `DJANGO_ALLOWED_HOSTS` | backend, nginx | Comma-separated |
| `DJANGO_CORS_ALLOWED_ORIGINS` | backend | Frontend origin(s) for dev (`http://localhost:5173`); empty in prod |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | backend, nginx | Required in prod for admin login |
| `POSTGRES_*` | backend, nginx | DB name/user/password/host/port |
| `DJANGO_SUPERUSER_*` | backend, nginx | Bootstraps admin in `start.sh` |
| `VITE_API_BASE_URL` | frontend | Dev: `http://localhost:8000/api`. Overridden to `/api` in the prod build |

## API endpoints

Knox tokens passed as `Authorization: Token <key>`. JSON in/out; file uploads on `JobFile` use multipart.

### Auth & health

| Method | Path | Auth | Notes |
|---|---|---|---|
| GET  | `/api/health/` | none | Liveness |
| POST | `/api/auth/register/` | none | `{username, email, password, [first_name, last_name]}` |
| POST | `/api/auth/login/` | none | `{username, password}` → `{token, expiry}` |
| POST | `/api/auth/logout/` | token | Invalidates current token |
| POST | `/api/auth/logoutall/` | token | Invalidates all user tokens |
| GET  | `/api/auth/me/` | token | Current user |

### Inspection (`/api/dahej/`)

Standard DRF `ModelViewSet` CRUD — `GET` (list), `POST` (create), `GET /{id}/` (retrieve), `PUT/PATCH /{id}/`, `DELETE /{id}/`.

| Resource | Path |
|---|---|
| Job types | `/api/dahej/job-types/` |
| Plants | `/api/dahej/plants/` |
| Jobs | `/api/dahej/jobs/` |
| Job files | `/api/dahej/job-files/` |
| Overtimes | `/api/dahej/overtimes/` |

Uploaded files are served from `/media/job_files/...`.

## Frontend

Routes are gated by the Knox token in Pinia. Once logged in, the user lands on the inspection views:

- `/jobs` — list, create, edit, mark done, attach files
- `/overtimes` — log and review OT entries
- `/job-types` — manage job-type master
- `/plants` — manage plant master
- `/profile` — current user

The axios client (`src/api/client.js`) attaches the auth token; the dahej API wrapper lives in `src/api/dahej.js`.

## Common Docker commands

Run inside any stack's directory.

```bash
docker compose ps
docker compose logs -f web
docker compose exec web python manage.py shell
docker compose exec web python manage.py makemigrations dahej_insp
docker compose exec web python manage.py migrate
docker compose exec db psql -U core -d core
docker compose down -v                                 # nuke volumes
docker compose build --no-cache
```

## Authentication flow (frontend)

1. Login form → POST `/api/auth/login/`
2. Knox returns `{token, expiry}` → stored in `localStorage` + Pinia
3. axios request interceptor attaches `Authorization: Token <key>`
4. 401 response → token cleared, redirect to `/login`
5. Router guard redirects unauthed users to `/login?next=<path>`

Token TTL: 10 hours with `AUTO_REFRESH=True`. Tunable in `backend/core/settings.py` under `REST_KNOX`.

## Troubleshooting

**`ModuleNotFoundError` after editing `requirements.txt`** — rebuild:
```bash
cd backend && docker compose up --build -d
```

**Vite shows blank page** — check container logs (`docker compose logs -f web`). For file changes not picked up on Windows, `usePolling: true` must be set in `vite.config.js`.

**CORS errors in dev** — `frontend/.env` `VITE_API_BASE_URL` and `backend/.env` `DJANGO_CORS_ALLOWED_ORIGINS` must agree on `http://localhost:5173`.

**"CSRF verification failed" on admin login (prod)** — add the browser URL to `DJANGO_CSRF_TRUSTED_ORIGINS` in `nginx/.env`.

**Uploaded file 404s in prod** — make sure nginx is proxying `/media/` to the Django container and the media volume is mounted on both `web` and `nginx`.

**Port already in use** — another stack is running. Dev: 5432/8000 (backend), 5173 (frontend). Prod: 80.

**Need a fresh DB / wipe uploaded files** — `./stop.sh --wipe && ./start.sh`. Destructive.
