from pathlib import Path

from app.config import settings
from app.licenses.merge import build_deployment_license
from app.models.deployment import Deployment
from app.models.license_file import LicenseFile
from app.models.license_server import LicenseServer
from app.models.validation_result import ValidationResult
from app.services.validation_service import validate_deployment

def generate_deployment_for_server(db, server_id: int):
    server = db.query(LicenseServer).filter(
        LicenseServer.id == server_id
    ).first()

    if not server:
        return None, {"error": "server not found"}

    license_files = db.query(LicenseFile).filter(
        LicenseFile.server_id == server_id
    ).order_by(
        LicenseFile.imported_at.asc()
    ).all()

    if not license_files:
        return None, {
            "error": "no license files found for server"
        }

    deployment_text = build_deployment_license(
        server,
        license_files,
    )

    deployments_base = settings["storage"]["deployments"]

    deployment = Deployment(
        server_id=server.id,
        artifact_path="pending",
        status="generated",
    )

    db.add(deployment)
    db.commit()
    db.refresh(deployment)

    artifact_dir = (
        Path(deployments_base) /
        str(server.id) /
        str(deployment.id)
    )

    artifact_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    artifact_path = artifact_dir / "license.dat"

    artifact_path.write_text(
        deployment_text,
        encoding="utf-8",
    )

    deployment.artifact_path = str(artifact_path)

    db.commit()
    db.refresh(deployment)

    validation_results = validate_deployment(
        deployment,
        server,
        deployment_text,
    )

    if any(
        item["severity"] == "error"
        for item in validation_results
    ):
        deployment.status = "invalid"

    elif validation_results:
        deployment.status = "warning"

    else:
        deployment.status = "valid"

    db.commit()

    for result in validation_results:
        db.add(
            ValidationResult(
                deployment_id=deployment.id,
                severity=result["severity"],
                code=result["code"],
                message=result["message"],
            )
        )

    db.commit()

    return deployment, None
