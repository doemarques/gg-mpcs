import tempfile
from pathlib import Path
from typing import Optional

import typer

from mcpctl import catalog as catalog_module
from mcpctl import github, installer, updater

app = typer.Typer(help="MCP distribution control CLI")
DEFAULT_SOURCE_REPOSITORY = "gn/mcps"


@app.command(name="list")
def list_command() -> None:
    mcps = catalog_module.load_catalog()
    for entry in catalog_module.list_mcps(mcps):
        typer.echo(f"{entry['name']}: version {entry.get('version')} path {entry.get('path')}")


@app.command(name="add")
def add_command(
    mcp_name: str,
    version: Optional[str] = typer.Option(
        None,
        "--version",
        help="Target MCP version (e.g. 1.2.0). Defaults to the catalog version.",
    ),
    source_repository: str = typer.Option(
        DEFAULT_SOURCE_REPOSITORY,
        "--source-repo",
        help="Source repository (owner/repo) hosting the MCP releases.",
    ),
    repo_root: str = typer.Option(".", "--repo", help="Path to the customer repository root."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview the distribution without writing files."),
) -> None:
    mcps = catalog_module.load_catalog()
    entries = catalog_module.list_mcps(mcps)
    entry = next((item for item in entries if item["name"] == mcp_name), None)
    if entry is None:
        raise typer.Exit(f"MCP '{mcp_name}' not found in catalog")

    version = version or entry.get("version")
    source_path = entry.get("path")
    tag = f"{mcp_name}/v{version}"
    commit = github.resolve_commit(source_repository, tag)
    tarball = github.download_archive(source_repository, commit)
    source_dir = github.extract_mcp(tarball, source_path, Path(tempfile.mkdtemp(prefix="mcpctl-")))

    result = installer.install_mcp(
        source_dir=source_dir,
        target_root=Path(repo_root),
        mcp_name=mcp_name,
        source_repository=source_repository,
        source_path=source_path,
        version=version,
        tag=tag,
        commit=commit,
        installed_path=source_path,
        dry_run=dry_run,
    )

    if dry_run:
        typer.echo(f"Would install {mcp_name} version {version} from {source_repository} at commit {commit}")
        typer.echo(f"Would copy {source_dir} -> {result['target']}")
    else:
        typer.echo(f"Installed {mcp_name} version {version} from {source_repository} at commit {commit}")
        typer.echo(f"Files: {', '.join(result['files'])}")


@app.command(name="update")
def update_command(
    mcp_name: str,
    version: Optional[str] = typer.Option(
        None,
        "--version",
        help="Target MCP version (e.g. 1.3.0). Defaults to the installed version.",
    ),
    source_repository: str = typer.Option(
        DEFAULT_SOURCE_REPOSITORY,
        "--source-repo",
        help="Source repository (owner/repo) hosting the MCP releases.",
    ),
    repo_root: str = typer.Option(".", "--repo", help="Path to the customer repository root."),
) -> None:
    lockfile = installer.lockfile_path(Path(repo_root))
    if not lockfile.exists():
        raise typer.Exit(f"No MCP lockfile found at {lockfile}")

    import yaml

    with open(lockfile, "r", encoding="utf-8") as lockfile_file:
        lock_data = yaml.safe_load(lockfile_file) or {}
    installed = (lock_data.get("mcps") or {}).get(mcp_name) or {}
    version = version or installed.get("version")
    if not version:
        raise typer.Exit(f"No installed version found for MCP '{mcp_name}'")

    source_path = installed.get("source_path") or f"mcps/{mcp_name}"
    source_repository = installed.get("source_repository") or DEFAULT_SOURCE_REPOSITORY
    result = updater.update_mcp(
        mcp_name=mcp_name,
        version=version,
        source_repository=source_repository,
        source_path=source_path,
        target_root=Path(repo_root),
    )
    typer.echo(f"Updated {mcp_name} version {version}")


@app.command(name="remove")
def remove_command(
    mcp_name: str,
    repo_root: str = typer.Option(".", "--repo", help="Path to the customer repository root."),
) -> None:
    lockfile = installer.lockfile_path(Path(repo_root))
    if not lockfile.exists():
        raise typer.Exit(f"No MCP lockfile found at {lockfile}")

    import yaml

    with open(lockfile, "r", encoding="utf-8") as lockfile_file:
        lock_data = yaml.safe_load(lockfile_file) or {}
    mcps = lock_data.get("mcps") or {}
    if mcp_name not in mcps:
        raise typer.Exit(f"MCP '{mcp_name}' is not installed")

    installed_path = mcps[mcp_name].get("installed_path") or f"mcps/{mcp_name}"
    import shutil

    destination = Path(repo_root) / installed_path
    if destination.exists():
        shutil.rmtree(destination)

    mcps.pop(mcp_name)
    lockfile.write_text(yaml.safe_dump({"mcps": mcps}, sort_keys=False), encoding="utf-8")
    typer.echo(f"Removed {mcp_name}")


def main() -> None:
    app()
