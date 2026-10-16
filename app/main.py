"""FastAPI application with password-gated, non-streaming inference."""
from pathlib import Path
from typing import Literal

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .auth import create_session, require_authenticated_request, verify_password
from .config import Settings, get_settings
from .llm_proxy import UpstreamInferenceError, infer

STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(title="LLM Inference Proxy", docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class LoginRequest(BaseModel):
    password: str = Field(min_length=1, max_length=1024)


class HistoryMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=20_000)


class InferenceRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=20_000)
    history: list[HistoryMessage] = Field(default_factory=list, max_length=20)


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
    messages = {401: "Authentication is required.", 422: "The request is invalid."}
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": str(exc.status_code), "message": messages.get(exc.status_code, "Request failed."), "details": None}},
    )


@app.get("/", include_in_schema=False)
@app.get("/workspace", include_in_schema=False)
async def serve_frontend() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/health")
async def health(settings: Settings = Depends(get_settings)) -> dict:
    return {"status": "ok", "services": {"inference": "configured" if settings.upstream_configured else "demo"}}


@app.post("/api/auth/login")
async def login(payload: LoginRequest, settings: Settings = Depends(get_settings)) -> dict:
    if not verify_password(payload.password, settings):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    session = create_session(settings)
    return {"authenticated": True, "token": session.token, "expiresAt": session.expires_at}


@app.post("/api/inference")
async def inference(
    payload: InferenceRequest,
    _: object = Depends(require_authenticated_request),
    settings: Settings = Depends(get_settings),
) -> dict:
    try:
        history = [{"role": item.role, "content": item.content} for item in payload.history]
        return {"response": await infer(payload.prompt, settings, history)}
    except UpstreamInferenceError as error:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY) from error
