from pathlib import Path
from typing import Any
import tempfile

from mcpctl import github, installer


def update_mcp(
    mcp_name: str,
    version: str,
    source_repository: str,
    source_path: str,
    target_root: Path,
    dry_run: bool = False,
) -> dict[str, Any]:
    tag = f"{mcp_name}/v{version}"
    commit = github.resolve_commit(source_repository, tag)
    tarball = github.download_archive(source_repository, commit)
    source_dir = github.extract_mcp(tarball, source_path, Path(tempfile.mkdtemp(prefix="mcpctl-")))
    return installer.install_mcp(
        source_dir=source_dir,
        target_root=target_root,
        mcp_name=mcp_name,
        source_repository=source_repository,
        source_path=source_path,
        version=version,
        tag=tag,
        commit=commit,
        installed_path=source_path,
        dry_run=dry_run,
    )
