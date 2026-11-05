from pathlib import Path
from typing import Any

import yaml

CATALOG_FILE = "catalog.yaml"


def load_catalog(path: Path | None = None) -> dict[str, Any]:
    catalog_path = path if path is not None else Path(CATALOG_FILE)
    with open(catalog_path, "r", encoding="utf-8") as catalog_file:
        data = yaml.safe_load(catalog_file) or {}
    return data.get("mcps") or {}


def list_mcps(catalog: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {"name": name, **config}
        for name, config in sorted(catalog.items())
    ]
