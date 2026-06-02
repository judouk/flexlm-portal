from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.audit import write_audit_event
from app.auth.dependencies import require_manager, require_user
from app.db import SessionLocal
from app.models.options_file import OptionsFile
from app.services.options_service import create_options_file, record_options_file, update_options_file

router = APIRouter()

class OptionsFileCreate(BaseModel):
    filename: str
    content: str


class OptionsFileUpdate(BaseModel):
    content: str


@router.post("/license-servers/{server_id}/options-files")
def create_options(
    server_id: int,
    data: OptionsFileCreate,
    user=Depends(require_manager),
):

    db = SessionLocal()

    options_file, error = create_options_file(
        db=db,
        server_id=server_id,
        filename=data.filename,
        content=data.content,
    )

    if error:
        db.close()
        return error

    write_audit_event(
        db,
        actor=user["sub"],
        action="options_file.created",
        object_type="options_file",
        object_id=options_file.id,
        details={
            "server_id": server_id,
            "filename": options_file.filename,
            "storage_path": options_file.storage_path,
        },
    )

    db.commit()

    response = {
        "id": options_file.id,
        "server_id": options_file.server_id,
        "filename": options_file.filename,
        "storage_path": options_file.storage_path,
        "created_at": options_file.created_at,
        "updated_at": options_file.updated_at,
    }

    db.close()

    return response

@router.get("/license-servers/{server_id}/options-files")
def list_options(
    server_id: int,
    user=Depends(require_user),
):

    db = SessionLocal()

    options_files = db.query(OptionsFile).filter(
        OptionsFile.server_id == server_id
    ).order_by(
        OptionsFile.updated_at.desc()
    ).all()

    response = [
        {
            "id": item.id,
            "server_id": item.server_id,
            "filename": item.filename,
            "storage_path": item.storage_path,
            "content_backend": item.content_backend,
            "content_ref": item.content_ref,
            "content_path": item.content_path,
            "created_at": item.created_at,
            "updated_at": item.updated_at,
        }
        for item in options_files
    ]

    db.close()

    return response

@router.get("/options-files/{options_file_id}")
def get_options(
    options_file_id: int,
    user=Depends(require_user),
):

    db = SessionLocal()

    options_file = db.query(OptionsFile).filter(
        OptionsFile.id == options_file_id
    ).first()

    if not options_file:
        db.close()
        return {"error": "options file not found"}

    response = {
        "id": options_file.id,
        "server_id": options_file.server_id,
        "filename": options_file.filename,
        "content": options_file.content,
        "storage_path": options_file.storage_path,
        "content_backend": options_file.content_backend,
        "content_ref": options_file.content_ref,
        "content_path": options_file.content_path,
        "created_at": options_file.created_at,
        "updated_at": options_file.updated_at,
        "published_at": options.published_at,
        "publish_status": options.publish_status,
        "publish_message": options.publish_message,
    }

    db.close()

    return response

@router.patch("/options-files/{options_file_id}")
def update_options(
    options_file_id: int,
    data: OptionsFileUpdate,
    user=Depends(require_manager),
):

    db = SessionLocal()

    options_file, error = update_options_file(
        db=db,
        options_file_id=options_file_id,
        content=data.content,
    )

    if error:
        db.close()
        return error

    write_audit_event(
        db,
        actor=user["sub"],
        action="options_file.updated",
        object_type="options_file",
        object_id=options_file.id,
        details={
            "server_id": options_file.server_id,
            "filename": options_file.filename,
            "storage_path": options_file.storage_path,
        },
    )

    db.commit()

    response = {
        "id": options_file.id,
        "server_id": options_file.server_id,
        "filename": options_file.filename,
        "storage_path": options_file.storage_path,
        "updated_at": options_file.updated_at,
    }

    db.close()

    return response


@router.post("/options-files/{options_file_id}/record")
def record_options(
    options_file_id: int,
    user=Depends(require_manager),
):

    db = SessionLocal()

    options_file, error = record_options_file(
        db=db,
        options_file_id=options_file_id,
    )

    if error:
        db.close()
        return error

    write_audit_event(
        db,
        actor=user["sub"],
        action="options_file.recorded",
        object_type="options_file",
        object_id=options_file.id,
        details={
            "content_backend": options_file.content_backend,
            "content_ref": options_file.content_ref,
            "content_path": options_file.content_path,
        },
    )

    db.commit()

    response = {
        "id": options_file.id,
        "server_id": options_file.server_id,
        "filename": options_file.filename,
        "content_backend": options_file.content_backend,
        "content_ref": options_file.content_ref,
        "content_path": options_file.content_path,
    }

    db.close()

    return response
