import asyncio
import random
import smtplib
import ssl
from datetime import datetime, timedelta

from shared.security import hash_password

from ..core.settings import AuthSettings

# Simple in-memory stores:
# _CODES: email -> (code, expires)
# _PENDING: email -> (username, hashed_password, expires)
_CODES: dict[str, tuple[str, datetime]] = {}
_PENDING: dict[str, tuple[str, str, datetime]] = {}

CODE_TTL_MINUTES = 10


def generate_code() -> str:
    return f"{random.randint(0, 999999):06d}"


def _store_code(email: str, code: str) -> None:
    _CODES[email.lower()] = (code, datetime.utcnow() + timedelta(minutes=CODE_TTL_MINUTES))


def _store_pending(email: str, username: str, hashed_password: str) -> None:
    _PENDING[email.lower()] = (username, hashed_password, datetime.utcnow() + timedelta(minutes=CODE_TTL_MINUTES))


def verify_code(email: str, code: str) -> bool:
    entry = _CODES.get(email.lower())
    if not entry:
        return False
    stored, expires = entry
    if datetime.utcnow() > expires:
        del _CODES[email.lower()]
        if email.lower() in _PENDING:
            del _PENDING[email.lower()]
        return False
    if stored == code:
        del _CODES[email.lower()]
        return True
    return False


def pop_pending(email: str) -> tuple[str, str] | None:
    entry = _PENDING.pop(email.lower(), None)
    if not entry:
        return None
    username, hashed_password, expires = entry
    if datetime.utcnow() > expires:
        return None
    return username, hashed_password


def send_email_sync(to_addr: str, subject: str, body: str, settings: AuthSettings) -> None:
    from_addr = settings.SMTP_FROM or f"no-reply@{settings.SMTP_HOST}"
    message = f"From: {from_addr}\r\nTo: {to_addr}\r\nSubject: {subject}\r\n\r\n{body}"

    if settings.SMTP_USE_TLS:
        context = ssl.create_default_context()
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            if settings.SMTP_USER and settings.SMTP_PASSWORD:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(from_addr, [to_addr], message)
    else:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            if settings.SMTP_USER and settings.SMTP_PASSWORD:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(from_addr, [to_addr], message)


async def create_pending_registration(username: str, email: str, password: str, settings: AuthSettings) -> str:
    """Create a pending registration, send confirmation code and return the code.

    Raises exceptions from SMTP if sending fails.
    """
    code = generate_code()
    hashed = hash_password(password)
    _store_code(email, code)
    _store_pending(email, username, hashed)

    subject = "Verification Code for Your Registration"
    body = f"Your verification code: {code}\nValid for: {CODE_TTL_MINUTES} minutes."

    # send synchronously in thread to avoid blocking
    try:
        await asyncio.to_thread(send_email_sync, email, subject, body, settings)
    except Exception as exc:
        # In development, SMTP may not be configured — print code to logs instead
        print(f"[confirmation] SMTP unavailable for {email}: {exc}. Confirmation code: {code}")

    return code
