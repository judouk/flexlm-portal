from pathlib import Path

from app.config import settings
from app.licenses.parser import parse_license
from app.models.license_file import Feature
from app.models.license_file import LicenseFile
from app.models.license_server import LicenseServer
from app.services.server_matching_server import match_server


def import_license_file(
    db,
    filename: str,
    content: bytes,
):

    parsed = parse_license(
        content.decode(
            "utf-8",
            errors="ignore",
        )
    )

    matched_server = None

    if parsed["server"]:
       matched_server, warning = (
           match_server(
               db,
               parsed,
           )
       )

    license_file = LicenseFile(
        server_id=matched_server.id if matched_server else None,
        filename=filename,
        vendor=",".join(parsed["vendors"]),
        server_hostname=parsed["server"]["hostname"]
            if parsed["server"] else None,
        server_hostid=parsed["server"]["hostid"]
            if parsed["server"] else None,
        matching_warning=warning,
    )

    if matched_server:
        license_file.server_id = matched_server.id

    for feature_data in parsed["features"]:

        feature = Feature(
            name=feature_data["name"],
            vendor=feature_data["vendor"],
            version=feature_data["version"],
            expiry=feature_data["expiry"],
            count=str(feature_data["count"]),
        )

        license_file.features.append(feature)

    db.add(license_file)

    db.commit()
    db.refresh(license_file)

    uploads_base = settings["storage"]["uploads"]

    storage_dir = (
        Path(uploads_base) /
        str(license_file.id)
    )

    storage_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    storage_path = storage_dir / filename

    storage_path.write_bytes(content)

    license_file.storage_path = str(storage_path)

    db.commit()
    db.refresh(license_file)

    return {
        "license_file": license_file,
        "matched_server": matched_server,
        "parsed": parsed,
    }
