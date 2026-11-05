import tempfile
import unittest
from pathlib import Path

import yaml

from mcpctl import installer


class InstallerTest(unittest.TestCase):
    def test_install_copies_files_and_writes_lockfile(self) -> None:
        source = Path(tempfile.mkdtemp())
        (source / "server.py").write_text("print('ok')", encoding="utf-8")
        target_root = Path(tempfile.mkdtemp())

        result = installer.install_mcp(
            source_dir=source,
            target_root=target_root,
            mcp_name="customer-data",
            source_repository="gn/mcps",
            source_path="mcps/customer-data",
            version="1.2.0",
            tag="customer-data/v1.2.0",
            commit="abc123",
            installed_path="mcps/customer-data",
        )

        self.assertTrue((target_root / "mcps/customer-data/server.py").exists())
        lockfile = target_root / "mcp-lock.yaml"
        self.assertTrue(lockfile.exists())
        lock_data = yaml.safe_load(lockfile.read_text(encoding="utf-8"))
        self.assertEqual(lock_data["mcps"]["customer-data"]["version"], "1.2.0")
        self.assertEqual(lock_data["mcps"]["customer-data"]["tag"], "customer-data/v1.2.0")
        self.assertEqual(lock_data["mcps"]["customer-data"]["commit"], "abc123")
        self.assertEqual(result["mcp"], "customer-data")

    def test_install_dry_run_does_not_write(self) -> None:
        source = Path(tempfile.mkdtemp())
        (source / "server.py").write_text("print('ok')", encoding="utf-8")
        target_root = Path(tempfile.mkdtemp())

        result = installer.install_mcp(
            source_dir=source,
            target_root=target_root,
            mcp_name="customer-data",
            source_repository="gn/mcps",
            source_path="mcps/customer-data",
            version="1.2.0",
            tag="customer-data/v1.2.0",
            commit="abc123",
            installed_path="mcps/customer-data",
            dry_run=True,
        )

        self.assertFalse((target_root / "mcps/customer-data").exists())
        self.assertFalse((target_root / "mcp-lock.yaml").exists())
        self.assertTrue(result["dry_run"])


if __name__ == "__main__":
    unittest.main()
