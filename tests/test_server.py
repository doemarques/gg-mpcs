import asyncio
import unittest

from gn_accelerators_chatbot_mcp import main
from gn_accelerators_chatbot_mcp.server import mcp


class ServerTest(unittest.TestCase):
    def test_server_instance_is_created(self) -> None:
        self.assertIsNotNone(mcp)

    def test_server_name(self) -> None:
        self.assertEqual(mcp.name, "gn-accelerators-chatbot-mcp")

    def test_main_is_callable(self) -> None:
        self.assertTrue(callable(main))


class ServerToolsTest(unittest.TestCase):
    def test_example_tools_are_registered(self) -> None:
        tools = asyncio.run(mcp.list_tools())
        names = {tool.name for tool in tools}
        self.assertIn("echo", names)
        self.assertIn("add", names)

    def test_echo_tool_returns_message(self) -> None:
        result = asyncio.run(mcp.call_tool("echo", {"message": "hello"}))
        self.assertFalse(result.is_error)
        self.assertEqual(result.structured_content["result"], "hello")

    def test_add_tool_returns_sum(self) -> None:
        result = asyncio.run(mcp.call_tool("add", {"a": 2, "b": 3}))
        self.assertFalse(result.is_error)
        self.assertEqual(result.structured_content["result"], 5)


if __name__ == "__main__":
    unittest.main()
