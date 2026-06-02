from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.auth.dependencies import require_user
from app.auth.ldap_provider import authenticate_ldap
from app.auth.security import create_access_token, verify_password
from app.config import settings
from app.db import SessionLocal
from app.models.user import User

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
def login(data: LoginRequest):

    provider = settings["auth"]["provider"]

    if provider == "ldap":
        result = authenticate_ldap(
            data.username,
            data.password,
        )

        if not result:
            raise HTTPException(
                status_code=401,
                detail="invalid credentials",
            )

        token = create_access_token({
            "sub": result["username"],
            "role": result["role"],
        })

        return {
            "access_token": token,
            "token_type": "bearer",
            "role": result["role"],
        }

    if provider != "local":
        raise HTTPException(
            status_code=400,
            detail=(
                f"/login not supported "
                f"for provider {provider}"
            ),
        )

    db = SessionLocal()

    user = db.query(User).filter(
        User.username == data.username
    ).first()

    if not user:
        db.close()
        raise HTTPException(
            status_code=401,
            detail="invalid credentials",
        )

    if not verify_password(
        data.password,
        user.password_hash,
    ):
        db.close()
        raise HTTPException(
            status_code=401,
            detail="invalid credentials",
        )

    if not user.active:
        db.close()
        raise HTTPException(
            status_code=403,
            detail="user disabled",
        )

    token = create_access_token({
        "sub": user.username,
        "role": user.role,
    })

    response = {
        "access_token": token,
        "token_type": "bearer",
        "role": user.role,
    }

    db.close()

    return response

@router.get("/me")
def me(user=Depends(require_user)):
    return user
