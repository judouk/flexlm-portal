from app.config import settings
from app.content.filesystem_backend import FilesystemContentBackend
from app.content.git_backend import GitContentBackend

def get_content_backend():
    backend = settings["content"]["backend"]

    if backend == "git":
        return GitContentBackend()

    if backend == "filesystem":
        return FilesystemContentBackend()

    raise ValueError(
        f"unsupported content backend: {backend}"
    )
