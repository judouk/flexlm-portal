from datetime import datetime
from pathlib import Path

from app.config import settings
from app.content.factory import get_content_backend
from app.models.license_server import LicenseServer
from app.models.options_file import OptionsFile

def write_options_file_to_storage(options_file):

    path = Path(options_file.storage_path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        options_file.content,
        encoding="utf-8",
    )

def create_options_file(
    db,
    server_id: int,
    filename: str,
    content: str,
):

    server = db.query(LicenseServer).filter(
        LicenseServer.id == server_id
    ).first()

    if not server:
        return None, {"error": "server not found"}

    options_base = settings["storage"]["options"]

    storage_path = (
        Path(options_base) /
        str(server.id) /
        filename
    )

    options_file = OptionsFile(
        server_id=server.id,
        filename=filename,
        storage_path=str(storage_path),
        content=content,
    )

    db.add(options_file)
    db.commit()
    db.refresh(options_file)

    write_options_file_to_storage(options_file)

    server.options_file_path = str(storage_path)

    db.commit()
    db.refresh(options_file)

    return options_file, None


def update_options_file(
    db,
    options_file_id: int,
    content: str,
):

    options_file = db.query(OptionsFile).filter(
        OptionsFile.id == options_file_id
    ).first()

    if not options_file:
        return None, {"error": "options file not found"}

    options_file.content = content
    options_file.updated_at = datetime.utcnow()

    write_options_file_to_storage(options_file)

    db.commit()
    db.refresh(options_file)

    return options_file, None

def record_options_file(
    db,
    options_file_id: int,
):

    options_file = db.query(OptionsFile).filter(
        OptionsFile.id == options_file_id
    ).first()

    if not options_file:
        return None, {"error": "options file not found"}

    if not options_file.storage_path:
        return None, {"error": "options file has no stored artifact"}

    backend = get_content_backend()

    target_path = (
        f"options/{options_file.server_id}/"
        f"{options_file.filename}"
    )

    result = backend.record_file(
        source_path=options_file.storage_path,
        target_path=target_path,
        message=(
            f"Record options file {options_file.filename} "
            f"for server {options_file.server_id}"
        ),
    )

    options_file.content_backend = result["backend"]
    options_file.content_ref = result["ref"]
    options_file.content_path = result["path"]

    db.commit()
    db.refresh(options_file)

    return options_file, None

