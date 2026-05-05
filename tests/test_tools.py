import unittest

from jarvis.config import AppConfig
from jarvis.tools import CalculatorTool, SystemInfoTool


class CalculatorToolTest(unittest.TestCase):
    def test_evaluates_expression(self) -> None:
        tool = CalculatorTool()

        result = tool.run({"expression": "17 * 24 + 8"})

        self.assertIn("416", result.output)

    def test_normalizes_natural_language_expression(self) -> None:
        tool = CalculatorTool()

        result = tool.run({"expression": "How much is 7 x 9?"})

        self.assertIn("Expression: 7 * 9", result.output)
        self.assertIn("Result: 63", result.output)

    def test_normalizes_word_based_operators(self) -> None:
        tool = CalculatorTool()

        result = tool.run({"expression": "Calculate 20 divided by 5 plus 1"})

        self.assertIn("Expression: 20 / 5 + 1", result.output)
        self.assertIn("Result: 5.0", result.output)


class SystemInfoToolTest(unittest.TestCase):
    def test_returns_config_summary(self) -> None:
        config = AppConfig()
        tool = SystemInfoTool(config=config, mode="text")

        result = tool.run({})

        self.assertIn("Mode: text", result.output)
        self.assertIn(f"LLM backend: {config.llm_backend}", result.output)
        self.assertIn(f"Assistant model: {config.assistant_model}", result.output)
        self.assertIn(f"Router model: {config.router_model}", result.output)


if __name__ == "__main__":
    unittest.main()
