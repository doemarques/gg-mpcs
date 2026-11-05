from pathlib import Path
from typing import Any
import shutil

import yaml

LOCKFILE_NAME = "mcp-lock.yaml"


def lockfile_path(repo_root: Path) -> Path:
    return repo_root / LOCKFILE_NAME


def write_lockfile(
    repo_root: Path,
    mcp_name: str,
    source_repository: str,
    source_path: str,
    version: str,
    tag: str,
    commit: str,
    installed_path: str,
) -> None:
    lockfile: dict[str, Any] = {
        "mcps": {
            mcp_name: {
                "source_repository": source_repository,
                "source_path": source_path,
                "version": version,
                "tag": tag,
                "commit": commit,
                "installed_path": installed_path,
            }
        }
    }
    path = lockfile_path(repo_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as lockfile_file:
        yaml.safe_dump(lockfile, lockfile_file, sort_keys=False)


def install_mcp(
    source_dir: Path,
    target_root: Path,
    mcp_name: str,
    source_repository: str,
    source_path: str,
    version: str,
    tag: str,
    commit: str,
    installed_path: str,
    dry_run: bool = False,
) -> dict[str, Any]:
    destination = target_root / installed_path
    files = [
        str(path.relative_to(source_dir))
        for path in sorted(source_dir.rglob("*"))
        if path.is_file()
    ]
    result = {
        "mcp": mcp_name,
        "source": str(source_dir),
        "target": str(destination),
        "source_repository": source_repository,
        "source_path": source_path,
        "version": version,
        "tag": tag,
        "commit": commit,
        "installed_path": installed_path,
        "dry_run": dry_run,
        "files": files,
    }
    if not dry_run:
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            shutil.rmtree(destination)
        shutil.copytree(source_dir, destination)
        write_lockfile(
            repo_root=target_root,
            mcp_name=mcp_name,
            source_repository=source_repository,
            source_path=source_path,
            version=version,
            tag=tag,
            commit=commit,
            installed_path=installed_path,
        )
    return result
