import tempfile
import unittest
from pathlib import Path

import yaml

from mcpctl import catalog


class CatalogTest(unittest.TestCase):
    def test_load_catalog_returns_mcps_mapping(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "catalog.yaml"
            path.write_text(
                yaml.safe_dump(
                    {
                        "mcps": {
                            "customer-data": {
                                "path": "mcps/customer-data",
                                "version": "1.2.0",
                            }
                        }
                    }
                ),
                encoding="utf-8",
            )
            mcps = catalog.load_catalog(path)
        self.assertEqual(mcps["customer-data"]["version"], "1.2.0")

    def test_list_mcps_returns_sorted_entries(self) -> None:
        mcps = {
            "ticket-management": {"path": "mcps/ticket-management", "version": "1.0.0"},
            "customer-data": {"path": "mcps/customer-data", "version": "1.2.0"},
        }
        entries = catalog.list_mcps(mcps)
        self.assertEqual([entry["name"] for entry in entries], ["customer-data", "ticket-management"])


if __name__ == "__main__":
    unittest.main()
