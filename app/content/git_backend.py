import shutil
import subprocess
from pathlib import Path

from app.config import settings
from app.content.base import ContentBackend


class GitContentBackend(ContentBackend):
    def __init__(self):
        self.repo_path = Path(
            settings["content"]["git"]["repo_path"]
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

        destination = self.repo_path / target_path

        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        shutil.copy2(
            source,
            destination,
        )

        relative_path = destination.relative_to(
            self.repo_path
        )

        subprocess.run(
            ["git", "add", str(relative_path)],
            cwd=self.repo_path,
            check=True,
        )

        commit_result = subprocess.run(
            ["git", "commit", "-m", message],
            cwd=self.repo_path,
            text=True,
            capture_output=True,
        )

        if commit_result.returncode != 0:
            output = (
                commit_result.stdout +
                commit_result.stderr
            )

            if "nothing to commit" not in output.lower():
                raise RuntimeError(output)

        commit_hash = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=self.repo_path,
            text=True,
        ).strip()

        return {
            "backend": "git",
            "ref": commit_hash,
            "path": str(relative_path),
        }

    def publish(self):

        push_result = subprocess.run(
            ["git", "push"],
            cwd=self.repo_path,
            text=True,
            capture_output=True,
        )

        output = (
            push_result.stdout +
            push_result.stderr
        )

        if push_result.returncode != 0:
            return {
                "backend": "git",
                "published": False,
                "message": output,
            }

        commit_hash = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=self.repo_path,
            text=True,
        ).strip()

        return {
            "backend": "git",
            "published": True,
            "ref": commit_hash,
            "message": output,
        }
