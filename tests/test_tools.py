import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from jarvis.config import AppConfig
from jarvis.tools import CalculatorTool, FileSearchTool, SystemInfoTool, ToolError


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

    def test_limits_expensive_exponentiation(self) -> None:
        tool = CalculatorTool()

        with self.assertRaisesRegex(ToolError, "Exponentiation is limited"):
            tool.run({"expression": "2 ** 100000"})


class SystemInfoToolTest(unittest.TestCase):
    def test_returns_config_summary(self) -> None:
        config = AppConfig()
        tool = SystemInfoTool(config=config, mode="text")

        result = tool.run({})

        self.assertIn("Mode: text", result.output)
        self.assertIn(f"Assistant model: {config.assistant_model}", result.output)
        self.assertIn(f"Router model: {config.router_model}", result.output)


class FileSearchToolTest(unittest.TestCase):
    def test_searches_within_configured_repo_root(self) -> None:
        with TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            file_path = repo_root / "example.txt"
            file_path.write_text("transcription code lives here\n", encoding="utf-8")

            tool = FileSearchTool(repo_root=repo_root)
            result = tool.run({"query": "transcription"})

            self.assertIn("example.txt", result.output)

    def test_falls_back_when_ripgrep_is_unavailable(self) -> None:
        with TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            file_path = repo_root / "fallback.txt"
            file_path.write_text("router fallback works\n", encoding="utf-8")

            tool = FileSearchTool(repo_root=repo_root)
            with patch("jarvis.tools.shutil.which", return_value=None):
                result = tool.run({"query": "fallback"})

            self.assertIn("fallback.txt", result.output)


if __name__ == "__main__":
    unittest.main()
