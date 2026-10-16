# Project Plan

**Status**: Approved
**Created**: 2026-10-14
**Mode**: NEW

---

## 1. Project Overview

**Goal**: Build a password-gated browser interface that sends non-streaming prompts through a Python server-side proxy to a configurable dummy LLM endpoint. The project is designed so that every module is independently testable.

**App Type**: Static + API

**API Login**: Yes

**Mode**: NEW

**Deployment Plan**: No deployment plan found

---

## 2. Inference API Proxy — Backend

| Component | Technology |
|-----------|-----------|
| **Language** | Python 3.12 |
| **Runtime** | CPython |
| **Package Manager** | pip |
| **Test Runner** | pytest |
| **Mocking Library** | unittest.mock |
| **Test Command** | pytest |
| **Orchestration** | docker-compose |

The FastAPI service serves the static frontend, validates the shared password using a server-side environment value, and handles all upstream calls. It loads `LLM_ENDPOINT_URL`, `LLM_API_KEY`, and `APP_PASSWORD` from `.env`. The browser receives only application responses; it never receives the upstream URL, API key, or expected password. The upstream adapter is non-streaming and isolated so the dummy endpoint can be replaced later.

---

## 3. Frontend — Web App

| Component | Technology |
|-----------|-----------|
| **Language** | JavaScript |
| **Framework** | Plain HTML, CSS, and JavaScript |
| **Package Manager** | None |
| **Test Runner** | Browser/manual smoke test |
| **Mocking Library** | None |
| **Test Command** | Manual browser smoke test |

The browser stores conversations and UI preferences in `localStorage`. After the API accepts a submitted password, the frontend persists the signed-in state locally until logout or browser storage is cleared. Client-side state is a convenience only: every inference request remains authenticated and authorized by the backend.

---

## 4. Services Required

| Azure Service | Role in App | Environment Variable | Default Value (Local) | Classification |
|---------------|------------|---------------------|----------------------|----------------|
| No Azure service required | The initial version uses a locally configured dummy LLM endpoint and has no server-side datastore. | `LLM_ENDPOINT_URL`, `LLM_API_KEY`, `APP_PASSWORD` | Values supplied only in server-side `.env` | Essential |

---

## 5. Prerequisites

### Run

| Tool | Service(s) | Installed | Version |
|------|------------|-----------|---------|
| Python | Inference API Proxy | ❓ | Unknown |
| pip | Inference API Proxy | ❓ | Unknown |

### Debug

| Tool | Service(s) | Installed | Version |
|------|------------|-----------|---------|
| Docker Desktop / Docker Compose | Inference API Proxy | ❓ | Unknown |
| VS Code Python extension (`ms-python.python`) | Inference API Proxy | ❓ | Unknown |

Double-check every ❓ tool is installed before proceeding.

---

## 6. Design System & UI

**Component Library**: Pico.css
**Style Direction**: A calm, focused inference workspace with a compact console feel, restrained blue accents, clear response hierarchy, and minimal visual distraction.
**Typography**: system-ui / Segoe UI Variable

### Color Palette

| Token | Hex | Usage |
|-------|-----|-------|
| `primary` | `#2457A6` | Send-prompt and sign-in actions, active navigation, and focus states. |
| `accent`  | `#14B8A6` | Inference-ready indicators and subtle response highlights. |
| `surface` | `#F6F8FB` | Application canvas and low-contrast workspace background. |
| `text`    | `#172033` | Prompts, generated answers, and primary interface labels. |
| `muted`   | `#667085` | Metadata, helper text, and timestamps. |
| `border`  | `#D9E0EA` | Composer, response cards, and panel separators. |

### Pages

| Page | Route | Purpose | Layout |
|------|-------|---------|--------|
| Sign In | `/` | Validate the shared password before enabling inference. | `header, hero, form, footer` |
| Inference Workspace | `/workspace` | Compose prompts, send a non-streaming request, and inspect responses kept locally. | `header, nav, main, split(card-list|form), actions` |

### Sample Content

Sign In — session state:
| Field | Value | Status |
|-------|-------|--------|
| Workspace access | Shared password | Required |
| Session persistence | Browser localStorage | Active after successful sign-in |
| Upstream credentials | Server-side `.env` | Never shown |

Inference Workspace — conversation:
| Prompt | Model response | Source | Status |
|--------|----------------|--------|--------|
| Summarize the purpose of a server-side inference proxy. | A proxy keeps upstream endpoint credentials outside the browser and centralizes validation. | Dummy endpoint | Complete |
| Give three checks before sending an LLM request. | Validate the prompt, confirm local sign-in, and verify the server has required configuration. | Dummy endpoint | Complete |
| Explain why this response is not streamed. | The initial integration waits for one complete upstream result before returning it to the browser. | Dummy endpoint | Complete |

---

## 7. Project Structure

```
a-llm-inference/
├── .azure/
│   ├── requirements.json
│   └── project-plan.md
├── .env.example                 # Names only; never committed secrets
├── .gitignore                   # Excludes .env and local artifacts
├── requirements.txt
├── app/
│   ├── main.py                  # FastAPI application and static-file serving
│   ├── config.py                # Server-side environment validation
│   ├── auth.py                  # Shared-password validation and request checks
│   ├── llm_proxy.py             # Non-streaming dummy endpoint adapter
│   └── static/
│       ├── index.html
│       ├── styles.css
│       └── app.js
└── tests/
    ├── test_auth.py
    ├── test_inference.py
    └── test_health.py
```

---

## 8. Route Definitions

| # | Method | Path | Description | Request Body | Response Body | Status Codes |
|---|--------|------|-------------|-------------|--------------|-------------|
| 1 | GET | `/api/health` | Confirms application configuration is available without revealing values. | — | `{ status, services }` | 200, 503 |
| 2 | POST | `/api/auth/login` | Validates the submitted shared password against the server-side environment value. | `{ password }` | `{ authenticated }` | 200, 401, 500 |
| 3 | POST | `/api/inference` | Validates local sign-in and proxies one non-streaming prompt to the dummy LLM endpoint. | `{ prompt }` | `{ response }` | 200, 401, 422, 502, 500 |

All errors use `{ "error": { "code", "message", "details" } }`. The server must redact configuration and upstream error details before returning an error to the browser.

---

## 9. Next Steps

1. Run **azure-project-scaffold** to execute this plan
2. Run **azure-project-integrate** to wire the frontend to live data, smoke-test the backend, and create the migrations
3. Run **azure-debug-plan** → **azure-debug-generate** for Docker emulators and VS Code debugging
4. Run the **azure-deploy** agent when ready; it uses **azure-app-onboard** for architecture, cost estimation, IaC generation, provisioning, and health verification