import sys
from pathlib import Path

from jwt import ExpiredSignatureError, InvalidTokenError

ROOT_DIRECTORY = Path(__file__).resolve().parents[3]
if str(ROOT_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(ROOT_DIRECTORY))

from shared.security import decode_jwt_token

__all__ = ["decode_jwt_token", "ExpiredSignatureError", "InvalidTokenError"]
