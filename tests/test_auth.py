from app.auth import verify_password
from app.config import Settings


def test_verify_password_accepts_exact_match():
    assert verify_password("correct", Settings(app_password="correct"))


def test_verify_password_rejects_wrong_match():
    assert not verify_password("incorrect", Settings(app_password="correct"))
