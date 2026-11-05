import io
import json
import tempfile
import zipfile
from pathlib import Path, PurePosixPath
from urllib.request import Request, urlopen

GITHUB_API_BASE = "https://api.github.com"
DEFAULT_SOURCE_REPOSITORY = "gn/mcps"
_TIMEOUT_SECONDS = 30.0


def _get_json(url: str) -> dict:
    request = Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": "mcpctl"})
    with urlopen(request, timeout=_TIMEOUT_SECONDS) as response:
        return json.loads(response.read().decode("utf-8"))


def resolve_commit(repo: str, ref: str) -> str:
    url = f"{GITHUB_API_BASE}/repos/{repo}/commits/{ref}"
    return str(_get_json(url)["sha"])


def download_archive(repo: str, commit: str) -> bytes:
    url = f"{GITHUB_API_BASE}/repos/{repo}/tarball/{commit}"
    request = Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": "mcpctl"})
    with urlopen(request, timeout=60.0) as response:
        return response.read()


def extract_mcp(tarball_bytes: bytes, mcp_path: str, dest: Path) -> Path:
    dest = dest.resolve()
    dest.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(io.BytesIO(tarball_bytes)) as archive:
        for member in archive.infolist():
            member_path = PurePosixPath(member.filename)
            if member_path.is_absolute() or ".." in member_path.parts:
                continue
            target = (dest / Path(*member_path.parts)).resolve()
            if dest not in target.parents and target != dest:
                continue
            archive.extract(member, dest)

    entries = [entry for entry in dest.iterdir() if entry.is_dir()]
    top_level = entries[0] if len(entries) == 1 else dest
    mcp_dir = top_level.joinpath(*PurePosixPath(mcp_path).parts)
    if not mcp_dir.is_dir():
        raise FileNotFoundError(f"MCP path not found in archive: {mcp_path}")
    return mcp_dir
