import unittest

from jarvis.router import LLMRouter, RouterError


class FakeLLMClient:
    def __init__(self, reply: str | None = None, error: Exception | None = None) -> None:
        self.reply = reply
        self.error = error

    def generate_reply(self, history: list[dict[str, str]]) -> str:
        if self.error is not None:
            raise self.error
        assert self.reply is not None
        return self.reply


class RouterTest(unittest.TestCase):
    def test_invalid_json_error_includes_raw_reply_preview(self) -> None:
        router = LLMRouter(
            llm_client=FakeLLMClient(reply="I think you should use the time tool."),
            confidence_threshold=0.75,
        )

        with self.assertRaises(RouterError) as context:
            router.decide(
                user_text="What time is it?",
                session_context="",
                tool_catalog=[],
            )

        self.assertIn("Raw reply:", str(context.exception))


if __name__ == "__main__":
    unittest.main()
