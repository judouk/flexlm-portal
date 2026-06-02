from fastapi import APIRouter
from fastapi import Depends
from pydantic import BaseModel

from app.auth.dependencies import require_admin
from app.auth.security import hash_password
from app.db import SessionLocal
from app.models.user import User


router = APIRouter()


class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "user"


@router.post("/users")
def create_user(
    data: UserCreate,
    admin=Depends(require_admin),
):

    db = SessionLocal()

    existing = db.query(User).filter(
        User.username == data.username
    ).first()

    if existing:
        db.close()
        return {"error": "user already exists"}

    user = User(
        username=data.username,
        password_hash=hash_password(data.password),
        role=data.role,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    response = {
        "id": user.id,
        "username": user.username,
        "role": user.role,
        "active": user.active,
    }

    db.close()

    return response
