from fastapi import APIRouter, Depends, File, UploadFile
from pathlib import Path
import shutil

from app.audit import write_audit_event
from app.auth.dependencies import require_admin, require_manager, require_user
from app.db import SessionLocal
from app.models.license_file import LicenseFile
from app.services.content_recording_service import record_license_file
from app.services.license_import_service import import_license_file

router = APIRouter()

@router.delete("/license-files/{license_file_id}")
def delete_license_file(
    license_file_id: int,
    user=Depends(require_admin),
):
    db = SessionLocal()

    license_file = db.query(LicenseFile).filter(
        LicenseFile.id == license_file_id
    ).first()

    if not license_file:
        db.close()
        return {"error": "license file not found"}

    storage_path = Path(license_file.storage_path)

    if storage_path.exists():
        shutil.rmtree(storage_path.parent, ignore_errors=True)

    write_audit_event(
        db,
        actor=user["sub"],
        action="license_file.deleted",
        object_type="license_file",
        object_id=license_file.id,
        details={
            "filename": license_file.filename,
            "storage_path": license_file.storage_path,
            "server_id": license_file.server_id,
        },
    )

    db.delete(license_file)
    db.commit()
    db.close()

    return {"id": license_file_id, "deleted": True}

@router.post("/license-files/import")
async def import_license(
    file: UploadFile = File(...),
    user=Depends(require_manager),
):

    content = await file.read()

    db = SessionLocal()

    result = import_license_file(
        db=db,
        filename=file.filename,
        content=content,
    )

    license_file = result["license_file"]
    matched_server = result["matched_server"]
    parsed = result["parsed"]

    recorded_license_file, record_error = record_license_file(
        db,
        license_file.id,
    )

    if record_error:
        license_file.publish_status = "record_failed"
        license_file.publish_message = record_error["error"]
    else:
        license_file = recorded_license_file

    write_audit_event(
        db,
        actor=user["sub"],
        action="license_file.imported",
        object_type="license_file",
        object_id=license_file.id,
        details={
            "filename": license_file.filename,
            "server_hostid": license_file.server_hostid,
            "content_backend": license_file.content_backend,
            "content_ref": license_file.content_ref,
            "content_path": license_file.content_path,
            "record_error": record_error,
        },
    )

    db.commit()

    response = {
        "license_file_id": license_file.id,
        "matched_server": {
            "id": matched_server.id,
            "name": matched_server.name,
            "hostname": matched_server.hostname,
            "hostid": matched_server.hostid,
        } if matched_server else None,
        "parsed": parsed,
        "storage_path": license_file.storage_path,
    }

    db.close()

    return response

@router.post("/license-files/{license_file_id}/record")
def record_license(
    license_file_id: int,
    user=Depends(require_manager),
):

    db = SessionLocal()

    license_file, error = record_license_file(
        db,
        license_file_id,
    )

    if error:
        db.close()
        return error

    write_audit_event(
        db,
        actor=user["sub"],
        action="license_file.recorded",
        object_type="license_file",
        object_id=license_file.id,
        details={
            "content_backend": license_file.content_backend,
            "content_ref": license_file.content_ref,
            "content_path": license_file.content_path,
        },
    )

    db.commit()

    response = {
        "id": license_file.id,
        "filename": license_file.filename,
        "content_backend": license_file.content_backend,
        "content_ref": license_file.content_ref,
        "content_path": license_file.content_path,
    }

    db.close()

    return response

@router.get("/license-files")
def list_license_files(
    user=Depends(require_user),
):

    db = SessionLocal()

    license_files = db.query(LicenseFile).order_by(
        LicenseFile.imported_at.desc()
    ).limit(200).all()

    response = [
        {
            "id": item.id,
            "server_id": item.server_id,
            "filename": item.filename,
            "vendor": item.vendor,
            "server_hostname": item.server_hostname,
            "server_hostid": item.server_hostid,
            "storage_path": item.storage_path,
            "imported_at": item.imported_at,
            "content_backend": item.content_backend,
            "content_ref": item.content_ref,
            "content_path": item.content_path,
            "feature_count": len(item.features),
            "published_at": item.published_at,
            "publish_status": item.publish_status,
            "publish_message": item.publish_message,
        }
        for item in license_files
    ]

    db.close()

    return response
