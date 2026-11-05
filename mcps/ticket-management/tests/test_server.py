import unittest

from ticket_management import main
from ticket_management.server import mcp


class TicketManagementServerTest(unittest.TestCase):
    def test_server_instance_is_created(self) -> None:
        self.assertIsNotNone(mcp)

    def test_server_name(self) -> None:
        self.assertEqual(mcp.name, "ticket-management")

    def test_main_is_callable(self) -> None:
        self.assertTrue(callable(main))


if __name__ == "__main__":
    unittest.main()
