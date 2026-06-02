import hashlib
import shutil
from pathlib import Path

from app.config import settings
from app.content.base import ContentBackend

class FilesystemContentBackend(ContentBackend):

    def __init__(self):
        self.base_path = Path(
            settings["content"]["filesystem"]["path"]
        )

    def record_file(
        self,
        source_path: str,
        target_path: str,
        message: str,
    ):

        source = Path(source_path)

        if not source.exists():
            raise FileNotFoundError(
                f"source file not found: {source_path}"
            )

        destination = self.base_path / target_path

        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        shutil.copy2(source, destination)

        digest = hashlib.sha256(
            destination.read_bytes()
        ).hexdigest()

        return {
            "backend": "filesystem",
            "ref": f"sha256:{digest}",
            "path": str(destination),
        }

    def publish(self):
        return {
            "backend": "filesystem",
            "published": True,
            "message": "filesystem backend does not require publishing",
        }
