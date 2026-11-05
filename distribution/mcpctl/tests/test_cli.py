import os
import tempfile
import unittest
from pathlib import Path

import yaml
from typer.testing import CliRunner

from mcpctl import cli

runner = CliRunner()


class CliTest(unittest.TestCase):
    def test_list_command(self) -> None:
        original_cwd = os.getcwd()
        with tempfile.TemporaryDirectory() as tmp_dir:
            Path(tmp_dir, "catalog.yaml").write_text(
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
            os.chdir(tmp_dir)
            try:
                result = runner.invoke(cli.app, ["list"])
            finally:
                os.chdir(original_cwd)
        self.assertEqual(result.exit_code, 0)
        self.assertIn("customer-data", result.output)

    def test_add_unknown_mcp_fails(self) -> None:
        result = runner.invoke(cli.app, ["add", "unknown-mcp"])
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("not found", result.output)


if __name__ == "__main__":
    unittest.main()
