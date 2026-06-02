from datetime import datetime

from app.content.factory import get_content_backend
from app.models.deployment import Deployment
from app.models.license_file import LicenseFile
from app.models.options_file import OptionsFile


def update_publish_state(item, result):

    item.published_at = datetime.utcnow()
    item.publish_status = (
        "published" if result.get("published") else "failed"
    )
    item.publish_message = result.get("message")


def publish_content(db):

    backend = get_content_backend()

    result = backend.publish()

    recorded_license_files = db.query(LicenseFile).filter(
        LicenseFile.content_ref.isnot(None),
        LicenseFile.publish_status.is_(None),
    ).all()

    recorded_deployments = db.query(Deployment).filter(
        Deployment.content_ref.isnot(None),
        Deployment.publish_status.is_(None),
    ).all()

    recorded_options_files = db.query(OptionsFile).filter(
        OptionsFile.content_ref.isnot(None),
        OptionsFile.publish_status.is_(None),
    ).all()

    for item in recorded_license_files:
        update_publish_state(item, result)

    for item in recorded_deployments:
        update_publish_state(item, result)

    for item in recorded_options_files:
        update_publish_state(item, result)

    db.commit()

    return {
        "backend": result.get("backend"),
        "published": result.get("published"),
        "message": result.get("message"),
        "ref": result.get("ref"),
        "updated": {
            "license_files": len(recorded_license_files),
            "deployments": len(recorded_deployments),
            "options_files": len(recorded_options_files),
        },
    }
