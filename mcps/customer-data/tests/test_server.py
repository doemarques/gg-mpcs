import unittest

from customer_data import main
from customer_data.server import mcp


class CustomerDataServerTest(unittest.TestCase):
    def test_server_instance_is_created(self) -> None:
        self.assertIsNotNone(mcp)

    def test_server_name(self) -> None:
        self.assertEqual(mcp.name, "customer-data")

    def test_main_is_callable(self) -> None:
        self.assertTrue(callable(main))


if __name__ == "__main__":
    unittest.main()
