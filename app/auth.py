"""Password verification and signed session tokens."""
import hashlib
import hmac
import secrets
import time
from dataclasses import dataclass

from fastapi import HTTPException, Request, status

from .config import Settings, get_settings


@dataclass(frozen=True)
class Session:
    token: str
    expires_at: int


_sessions: dict[str, Session] = {}


def verify_password(submitted_password: str, settings: Settings) -> bool:
    """Compare passwords without timing leaks."""
    return hmac.compare_digest(submitted_password, settings.app_password)


def create_session(settings: Settings) -> Session:
    _purge_expired_sessions()
    token = secrets.token_urlsafe(32)
    session = Session(token=token, expires_at=int(time.time()) + settings.session_ttl_seconds)
    _sessions[token] = session
    return session


def _purge_expired_sessions() -> None:
    now = int(time.time())
    for token, session in list(_sessions.items()):
        if session.expires_at <= now:
            del _sessions[token]


def require_authenticated_request(request: Request) -> Session:
    """Require an unexpired bearer token issued after password verification."""
    authorization = request.headers.get("Authorization", "")
    scheme, _, token = authorization.partition(" ")
    session = _sessions.get(token) if scheme.lower() == "bearer" else None
    if not session or session.expires_at <= int(time.time()):
        if token:
            _sessions.pop(token, None)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication is required.",
        )
    return session


def token_fingerprint(token: str) -> str:
    """A safe diagnostic fingerprint; never log bearer tokens."""
    return hashlib.sha256(token.encode()).hexdigest()[:12]
