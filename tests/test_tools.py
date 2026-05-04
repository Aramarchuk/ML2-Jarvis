import unittest

from jarvis.config import AppConfig
from jarvis.tools import CalculatorTool, SystemInfoTool


class CalculatorToolTest(unittest.TestCase):
    def test_evaluates_expression(self) -> None:
        tool = CalculatorTool()

        result = tool.run({"expression": "17 * 24 + 8"})

        self.assertIn("416", result.output)


class SystemInfoToolTest(unittest.TestCase):
    def test_returns_config_summary(self) -> None:
        config = AppConfig()
        tool = SystemInfoTool(config=config, mode="text")

        result = tool.run({})

        self.assertIn("Mode: text", result.output)
        self.assertIn(config.ollama_model, result.output)


if __name__ == "__main__":
    unittest.main()
