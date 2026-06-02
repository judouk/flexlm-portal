from app.auth.security import hash_password
from app.db import Base
from app.db import SessionLocal
from app.db import engine
from app.models.user import User

Base.metadata.create_all(bind=engine)

db = SessionLocal()

username = "admin"
password = "admin"

existing = db.query(User).filter(
    User.username == username
).first()

if existing:
    print("admin user already exists")
else:
    user = User(
        username=username,
        password_hash=hash_password(password),
        role="admin",
    )

    db.add(user)
    db.commit()

    print("created admin/admin")

db.close()
