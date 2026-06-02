from fastapi import Depends, Header, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from jose import JWTError, jwt

from app.auth.provider import parse_groups, role_from_groups
from app.auth.security import ALGORITHM, SECRET_KEY
from app.config import settings

security = HTTPBearer(auto_error=False)

def get_user_from_token(
    credentials: HTTPAuthorizationCredentials | None,
):
    if not credentials:
        return None

    token = credentials.credentials

    try:
        return jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="invalid token",
        )


def get_user_from_headers(
    x_remote_user: str | None = Header(default=None),
    x_remote_email: str | None = Header(default=None),
    x_remote_groups: str | None = Header(default=None),
):
    if not x_remote_user:
        return None

    groups = parse_groups(x_remote_groups)

    return {
        "sub": x_remote_user,
        "email": x_remote_email,
        "groups": groups,
        "role": role_from_groups(groups),
        "auth_provider": "header",
    }


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    header_user=Depends(get_user_from_headers),
):
    provider = settings["auth"]["provider"]

    if provider == "header":
        if not header_user:
            raise HTTPException(
                status_code=401,
                detail="missing trusted auth headers",
            )

        return header_user

    token_user = get_user_from_token(credentials)

    if token_user:
        return token_user

    raise HTTPException(
        status_code=401,
        detail="not authenticated",
    )


def require_user(user=Depends(get_current_user)):
    return user


def require_manager(user=Depends(get_current_user)):
    if user["role"] not in ["manager", "admin"]:
        raise HTTPException(
            status_code=403,
            detail="manager role required",
        )

    return user


def require_admin(user=Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="admin role required",
        )

    return user
