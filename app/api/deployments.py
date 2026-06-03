from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse
from pathlib import Path
import shutil

from app.audit import write_audit_event
from app.auth.dependencies import require_admin, require_manager, require_user
from app.db import SessionLocal
from app.models.deployment import Deployment
from app.models.validation_result import ValidationResult
from app.services.content_recording_service import record_deployment
from app.services.deployment_service import generate_deployment_for_server

router = APIRouter()

@router.delete("/deployments/{deployment_id}")
def delete_deployment(
    deployment_id: int,
    user=Depends(require_admin),
):
    db = SessionLocal()

    deployment = db.query(Deployment).filter(
        Deployment.id == deployment_id
    ).first()

    if not deployment:
        db.close()
        return {"error": "deployment not found"}

    artifact_path = Path(deployment.artifact_path)

    if artifact_path.exists():
        shutil.rmtree(artifact_path.parent, ignore_errors=True)

    write_audit_event(
        db,
        actor=user["sub"],
        action="deployment.deleted",
        object_type="deployment",
        object_id=deployment.id,
        details={
            "artifact_path": deployment.artifact_path,
            "server_id": deployment.server_id,
        },
    )

    deployment.deleted_at = datetime.utcnow()
    deployment.deleted_by = user["sub"]

    write_audit_event(
        db,
        actor=user["sub"],
        action="deployment.deleted",
        object_type="deployment",
        object_id=deployment.id,
        details={
            "artifact_path": deployment.artifact_path,
            "server_id": deployment.server_id,
        },
    )

    db.commit()
    db.close()

    return {"id": deployment_id, "deleted": True}

@router.post(
    "/license-servers/{server_id}/generate-deployment"
)
def generate_deployment(
    server_id: int,
    user=Depends(require_manager),
):

    db = SessionLocal()

    deployment, error = generate_deployment_for_server(
        db,
        server_id,
    )

    if error:
        db.close()
        return error

    recorded_deployment, record_error = record_deployment(
        db,
        deployment.id,
    )

    if record_error:
        deployment.publish_status = "record_failed"
        deployment.publish_message = record_error["error"]
    else:
        deployment = recorded_deployment

    write_audit_event(
        db,
        actor=user["sub"],
        action="deployment.generated",
        object_type="deployment",
        object_id=deployment.id,
        details={
            "server_id": server_id,
            "artifact_path": deployment.artifact_path,
            "content_backend": deployment.content_backend,
            "content_ref": deployment.content_ref,
            "content_path": deployment.content_path,
            "record_error": record_error,
        },
    )

    db.commit()

    response = {
        "deployment_id": deployment.id,
        "server_id": deployment.server_id,
        "artifact_path": deployment.artifact_path,
        "status": deployment.status,
        "generated_at": deployment.generated_at,
    }

    db.close()

    return response


@router.get(
    "/deployments/{deployment_id}/artifact",
    response_class=PlainTextResponse,
)
def get_deployment_artifact(
    deployment_id: int,
    user=Depends(require_user),
):
    db = SessionLocal()

    deployment = db.query(Deployment).filter(
        Deployment.id == deployment_id
    ).first()

    if not deployment:
        db.close()
        raise HTTPException(
            status_code=404,
            detail="deployment not found",
        )

    artifact_path = Path(deployment.artifact_path)

    if not artifact_path.exists():
        db.close()
        raise HTTPException(
            status_code=404,
            detail="deployment artifact not found",
        )

    content = artifact_path.read_text(
        encoding="utf-8",
        errors="ignore",
    )

    db.close()

    return content

@router.post("/deployments/{deployment_id}/record")
def record_deployment_artifact(
    deployment_id: int,
    user=Depends(require_manager),
):

    db = SessionLocal()

    deployment, error = record_deployment(
        db,
        deployment_id,
    )

    if error:
        db.close()
        return error

    write_audit_event(
        db,
        actor=user["sub"],
        action="deployment.recorded",
        object_type="deployment",
        object_id=deployment.id,
        details={
            "content_backend": deployment.content_backend,
            "content_ref": deployment.content_ref,
            "content_path": deployment.content_path,
        },
    )

    db.commit()

    response = {
        "id": deployment.id,
        "server_id": deployment.server_id,
        "status": deployment.status,
        "content_backend": deployment.content_backend,
        "content_ref": deployment.content_ref,
        "content_path": deployment.content_path,
    }

    db.close()

    return response

@router.get("/deployments")
def list_deployments(
    user=Depends(require_user),
):

    db = SessionLocal()

    deployments = db.query(Deployment).filter(
        Deployment.deleted_at.is_(None)
    ).order_by(
        Deployment.generated_at.desc()
    ).limit(200).all()

    response = [
        {
            "id": item.id,
            "server_id": item.server_id,
            "artifact_path": item.artifact_path,
            "status": item.status,
            "generated_at": item.generated_at,
            "content_backend": item.content_backend,
            "content_ref": item.content_ref,
            "content_path": item.content_path,
            "published_at": item.published_at,
            "publish_status": item.publish_status,
            "publish_message": item.publish_message,
        }
        for item in deployments
    ]

    db.close()

    return response

@router.get("/deployments/{deployment_id}/validation")
def deployment_validation(
    deployment_id: int,
    user=Depends(require_user),
):

    db = SessionLocal()

    results = (
        db.query(ValidationResult)
        .filter(
            ValidationResult.deployment_id
            == deployment_id
        )
        .all()
    )

    response = [
        {
            "severity": item.severity,
            "code": item.code,
            "message": item.message,
            "created_at": item.created_at,
        }
        for item in results
    ]

    db.close()

    return response
