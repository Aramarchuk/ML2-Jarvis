import unittest

from jarvis.config import AppConfig


class ConfigParsingTest(unittest.TestCase):
    def test_uses_documented_defaults(self) -> None:
        config = AppConfig()

        self.assertEqual(config.llm_base_url, "https://hub.nhr.fau.de/api/llmgw/v1")
        self.assertEqual(config.assistant_model, "Qwen/Qwen3.5-35B-A3B-FP8")
        self.assertEqual(config.router_model, "IBM/granite-4.0-micro")


if __name__ == "__main__":
    unittest.main()
