from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.auth.dependencies import require_admin, require_user
from app.db import SessionLocal
from app.models.license_daemon import LicenseDaemon
from app.models.license_server import LicenseServer


router = APIRouter()

class LicenseDaemonCreate(BaseModel):
    name: str
    daemon_path: str | None = None
    options_file_path: str | None = None
    port: int | None = None
    served_vendors: str | None = None

class LicenseServerCreate(BaseModel):
    name: str
    hostname: str
    hostid: str

    lmgrd_port: int | None = None

    merge_policy: str = "additive"

@router.post("/license-servers")
def create_license_server(
    data: LicenseServerCreate,
    admin=Depends(require_admin),
):

    db = SessionLocal()

    server = LicenseServer(
        name=data.name,
        hostname=data.hostname,
        hostid=data.hostid,
        lmgrd_port=data.lmgrd_port,
        merge_policy=data.merge_policy,
    )

    db.add(server)
    db.commit()
    db.refresh(server)

    response = {
        "id": server.id,
        "name": server.name,
        "hostname": server.hostname,
        "hostid": server.hostid,
        "merge_policy": server.merge_policy,
    }

    db.close()

    return response

@router.post("/license-servers/{server_id}/daemons")
def create_license_daemon(
    server_id: int,
    data: LicenseDaemonCreate,
    admin=Depends(require_admin),
):
    db = SessionLocal()

    server = db.query(LicenseServer).filter(
        LicenseServer.id == server_id
    ).first()

    if not server:
        db.close()
        return {"error": "license server not found"}

    daemon = LicenseDaemon(
        server_id=server.id,
        name=data.name,
        daemon_path=data.daemon_path,
        options_file_path=data.options_file_path,
        port=data.port,
        served_vendors=data.served_vendors,
    )

    db.add(daemon)
    db.commit()
    db.refresh(daemon)

    response = {
        "id": daemon.id,
        "server_id": daemon.server_id,
        "name": daemon.name,
        "daemon_path": daemon.daemon_path,
        "options_file_path": daemon.options_file_path,
        "port": daemon.port,
        "served_vendors": daemon.served_vendors,
    }

    db.close()

    return response

@router.get("/license-servers")
def list_license_servers(
    user=Depends(require_user),
):

    db = SessionLocal()

    servers = db.query(LicenseServer).order_by(
        LicenseServer.name.asc()
    ).all()

    response = [
        {
            "id": server.id,
            "name": server.name,
            "hostname": server.hostname,
            "hostid": server.hostid,
            "lmgrd_port": server.lmgrd_port,
            "merge_policy": server.merge_policy,
        }
        for server in servers
    ]

    db.close()

    return response

@router.get("/license-servers/{server_id}/daemons")
def list_license_daemons(
    server_id: int,
    user=Depends(require_user),
):
    db = SessionLocal()

    daemons = db.query(LicenseDaemon).filter(
        LicenseDaemon.server_id == server_id
    ).order_by(
        LicenseDaemon.name.asc()
    ).all()

    response = [
        {
            "id": daemon.id,
            "server_id": daemon.server_id,
            "name": daemon.name,
            "daemon_path": daemon.daemon_path,
            "options_file_path": daemon.options_file_path,
            "port": daemon.port,
            "served_vendors": daemon.served_vendors,
        }
        for daemon in daemons
    ]

    db.close()

    return response

@router.delete("/license-daemons/{daemon_id}")
def delete_license_daemon(
    daemon_id: int,
    admin=Depends(require_admin),
):
    db = SessionLocal()

    daemon = db.query(LicenseDaemon).filter(
        LicenseDaemon.id == daemon_id
    ).first()

    if not daemon:
        db.close()
        return {"error": "license daemon not found"}

    response = {
        "id": daemon.id,
        "server_id": daemon.server_id,
        "name": daemon.name,
        "deleted": True,
    }

    db.delete(daemon)
    db.commit()
    db.close()

    return response
