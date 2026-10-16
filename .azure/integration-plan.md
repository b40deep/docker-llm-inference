# Integration Plan

## Backend
- Folder: `app/`
- Run: `python -m uvicorn app.main:app --reload`
- Port: `8000`
- Build/validation: `python -m pytest`
- Health endpoint: `GET /api/health`

## Frontend
- Folder: `app/static/`
- No separate frontend build; FastAPI serves static files.
- Development is included in the backend run command.
- API seam: `app/static/app.js`, function `api(path, options)`.
- No mock-client files or mock datasets exist. The safe server-side demo behavior is in `app/llm_proxy.py` and must not be copied to the browser.

## API routes
- `GET /api/health`
- `POST /api/auth/login` body `{ password }`
- `POST /api/inference` body `{ prompt }`, requires `Authorization: Bearer <token>`

## Database
- No database is used in this approved scaffold.
- No migrations or seed data are required. Explicitly do not add seed data.
- Browser response data is stored in `localStorage` under `llmInference.responses`.

## Shared types
- No shared package. Client request/response shapes are intentionally small and local to `app/static/app.js`.

## Services
- Essential: FastAPI inference proxy; server-side `.env` configuration.
- Enhancement: configured OpenAI-compatible upstream endpoint.

## Integration checklist
1. Smoke-test health, login rejection/acceptance, authenticated inference, and demo fallback.
2. Keep the inference proxy server-side and ensure upstream secrets remain absent from static assets and API responses.
3. Verify the localStorage session/response behavior in a browser.
4. No database migration or seeding work applies to this project.
