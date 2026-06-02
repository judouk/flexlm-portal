from fastapi import FastAPI

from app.api import audit, auth, content, deployments, license_files, license_servers, options_files, users

from app.db import Base, engine

from app.models.audit_event import AuditEvent
from app.models.deployment import Deployment
from app.models.license_daemon import LicenseDaemon
from app.models.license_file import Feature, LicenseFile
from app.models.license_server import LicenseServer
from app.models.options_file import OptionsFile
from app.models.user import User
from app.models.validation_result import ValidationResult

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="FlexLM Portal v2",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(audit.router)
app.include_router(auth.router)
app.include_router(content.router)
app.include_router(deployments.router)
app.include_router(license_files.router)
app.include_router(license_servers.router)
app.include_router(options_files.router)
app.include_router(users.router)

Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {
        "application": "flexlm-portal-v2",
        "status": "running",
    }
