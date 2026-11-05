import unittest

from document_search import main
from document_search.server import mcp


class DocumentSearchServerTest(unittest.TestCase):
    def test_server_instance_is_created(self) -> None:
        self.assertIsNotNone(mcp)

    def test_server_name(self) -> None:
        self.assertEqual(mcp.name, "document-search")

    def test_main_is_callable(self) -> None:
        self.assertTrue(callable(main))


if __name__ == "__main__":
    unittest.main()
