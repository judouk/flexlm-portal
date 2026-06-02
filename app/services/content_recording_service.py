from pathlib import Path

from app.content.factory import get_content_backend
from app.models.deployment import Deployment
from app.models.license_file import LicenseFile


def record_license_file(db, license_file_id: int):

    license_file = db.query(LicenseFile).filter(
        LicenseFile.id == license_file_id
    ).first()

    if not license_file:
        return None, {"error": "license file not found"}

    if not license_file.storage_path:
        return None, {
            "error": "license file has no stored artifact"
        }

    target_path = (
        f"uploads/{license_file.server_hostid}/"
        f"{license_file.id}/"
        f"{license_file.filename}"
    )

    backend = get_content_backend()

    result = backend.record_file(
        source_path=license_file.storage_path,
        target_path=target_path,
        message=(
            f"Record uploaded license file "
            f"{license_file.filename}"
        ),
    )

    license_file.content_backend = result["backend"]
    license_file.content_ref = result["ref"]
    license_file.content_path = result["path"]

    db.commit()
    db.refresh(license_file)

    return license_file, None


def record_deployment(db, deployment_id: int):

    deployment = db.query(Deployment).filter(
        Deployment.id == deployment_id
    ).first()

    if not deployment:
        return None, {"error": "deployment not found"}

    source_path = Path(deployment.artifact_path)

    if not source_path.exists():
        return None, {
            "error": "deployment artifact missing"
        }

    target_path = (
        f"deployments/{deployment.server_id}/"
        f"deployment-{deployment.id}/"
        f"license.dat"
    )

    backend = get_content_backend()

    result = backend.record_file(
        source_path=str(source_path),
        target_path=target_path,
        message=(
            f"Record deployment artifact "
            f"{deployment.id} for server {deployment.server_id}"
        ),
    )

    deployment.content_backend = result["backend"]
    deployment.content_ref = result["ref"]
    deployment.content_path = result["path"]
    deployment.status = "recorded"

    db.commit()
    db.refresh(deployment)

    return deployment, None
