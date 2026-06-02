from datetime import datetime
from datetime import timedelta

from jose import jwt
from passlib.context import CryptContext

from app.config import settings


SECRET_KEY = settings["security"]["secret_key"]
ALGORITHM = settings["security"]["algorithm"]
ACCESS_TOKEN_MINUTES = settings["security"]["access_token_minutes"]


pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto",
)


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str):
    return pwd_context.verify(password, password_hash)


def create_access_token(data: dict):

    payload = data.copy()

    expires = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_MINUTES,
    )

    payload.update({"exp": expires})

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )
