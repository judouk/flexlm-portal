from pathlib import Path

from app.licenses.summary import aggregate_licence_summary
from app.licenses.summary import is_current_licence
from app.licenses.summary import select_latest_feature_entries
from app.licenses.summary import summarise_licence_text
from app.models.license_file import LicenseFile
from app.models.license_server import LicenseServer


def get_public_license_summary(db):
    servers = {
        server.id: server.name
        for server in db.query(LicenseServer).all()
    }

    license_files = db.query(LicenseFile).filter(
        LicenseFile.deleted_at.is_(None)
    ).order_by(
        LicenseFile.imported_at.asc()
    ).all()

    sources = []

    for license_file in license_files:
        if not license_file.storage_path:
            continue

        path = Path(license_file.storage_path)
        if not path.is_file():
            continue

        server_name = (
            servers.get(license_file.server_id)
            or license_file.server_hostname
            or "Unassigned"
        )

        text = path.read_text(
            encoding="utf-8",
            errors="ignore",
        )

        sources.append(
            {
                "license_server": server_name,
                "license_file_id": license_file.id,
                "imported_at": license_file.imported_at,
                "items": summarise_licence_text(text),
            }
        )

    entries = [
        item
        for item in select_latest_feature_entries(sources)
        if is_current_licence(item)
    ]

    return aggregate_licence_summary(entries)
