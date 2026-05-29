# TokenCast 2.0

An AI-powered platform for turning any screen into a programmable dashboard.
Built around four entities — **User → Display → Layout → Widget** — with a
plugin-based widget system so new widget types are added without touching the
core schema or endpoints.

## Stack

- **Backend:** FastAPI, SQLAlchemy 2.x, Alembic, Pydantic v2, JWT auth, Redis + WebSockets
- **Frontend:** Next.js 16 (App Router), React 19, TypeScript, TailwindCSS, TanStack Query, Zustand
- **Database:** PostgreSQL · **Realtime:** Redis pub/sub · **Infra:** Docker Compose

## Quick start

```bash
cp backend/.env.example backend/.env   # then set SECRET_KEY
docker compose up --build
```

- Frontend: http://localhost:3000
- API docs (Swagger): http://localhost:8000/docs
- The backend waits for Postgres, runs Alembic migrations, seeds system
  templates, then serves the API.

### Run the backend without Docker (uses SQLite, zero external services)

```bash
cd backend
pip install -r requirements.txt
DATABASE_URL="sqlite:///./dev.db" uvicorn app.main:app --reload
```

In development the app creates tables automatically and the AI builder + realtime
layer both degrade gracefully when no OpenAI key / Redis is present.

## Architecture

```
backend/app/
  core/        config, database, security, exceptions, realtime, seed
  models/      User, Display, Layout, Widget, Template  (SQLAlchemy 2.x)
  schemas/     Pydantic v2 request/response models
  repositories/ data-access layer (repository pattern)
  services/    business logic (auth, display, layout, widget, template, ai_builder)
  widgets/     plugin registry + widget definitions
  api/v1/      REST endpoints + WebSocket
```

Request flow: **endpoint → service → repository → model**. Services raise domain
exceptions that an app-level handler maps to HTTP responses, so the business
layer never imports FastAPI.

### Adding a widget (no core changes)

Create `backend/app/widgets/definitions/my_widget.py`, register a
`WidgetDefinition` with a Pydantic config model, import it in
`app/widgets/__init__.py`, and add a renderer to
`frontend/src/widgets/index.tsx`. The catalog endpoint, AI builder, validation,
and builder palette pick it up automatically.

## Widgets included

clock · weather · photo · video · custom_html · crypto_price · tradingview ·
watchlist · wallet_tracker · neural_trend · nft_gallery · telegram_feed ·
discord_feed

## Authentication

Email/password with JWT access + refresh tokens and a password-reset flow. The
`User` model carries `auth_provider` / `provider_subject` columns so Google and
wallet login can be added later without a migration.

## AI Layout Builder

`POST /api/v1/ai/build` with `{"prompt": "Build me a crypto trading command
center"}` returns a theme, grid and positioned widgets, and (by default) saves a
real layout. With no `AI_API_KEY` set it uses a deterministic keyword planner;
set a key (any OpenAI-compatible endpoint) to use an LLM, with automatic
fallback to the built-in planner on error.

---

## Build & verification status (honest accounting)

**Backend — verified in this environment:**
- Full app imports and boots; the entire API was exercised end-to-end against
  SQLite: register/login/refresh/password-reset, dashboard stats, display
  CRUD + assign + player view + heartbeat, layout CRUD + clone, widget
  add/update/delete with registry validation, template seeding + instantiation,
  and the AI builder producing & saving a layout. Auth/permission rejections
  (401/404) confirmed.
- Alembic migration applies and reverses cleanly (validated on SQLite).

**Frontend — written and syntax-checked, NOT built:**
- All 17 TS/TSX source files pass esbuild syntax validation. They have **not**
  been type-checked against React/Next types or run through `next build` in this
  environment, so expect to shake out type/import issues on first `npm install
  && npm run build`.

**Docker — config written, NOT run:**
- `docker-compose.yml` is valid YAML and `entrypoint.sh` passes `bash -n`, but
  no Docker daemon was available here, so `docker compose up` was not executed.

**Known next steps / not yet implemented:**
- Data-source widgets (NFT/Telegram/Discord/neural-trend/wallet) render
  presentational shells on the frontend; their live data fetchers and the
  corresponding backend proxy integrations are stubs to be filled in.
- Device pairing UI, display grouping UI, and tests are not yet built.
