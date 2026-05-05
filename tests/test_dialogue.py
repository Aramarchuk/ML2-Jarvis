import unittest

from jarvis.dialogue import DialogueManager


class DialogueManagerTest(unittest.TestCase):
    def test_initializes_with_system_message(self) -> None:
        dialogue = DialogueManager(system_prompt="System message")

        self.assertEqual(
            dialogue.build_messages(),
            [{"role": "system", "content": "System message"}],
        )

    def test_appends_messages_in_order(self) -> None:
        dialogue = DialogueManager(system_prompt="System message")
        dialogue.append_message("user", "Hello")
        dialogue.append_message("assistant", "Hi")

        self.assertEqual(
            dialogue.build_messages(),
            [
                {"role": "system", "content": "System message"},
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi"},
            ],
        )

    def test_merges_context_into_first_system_message(self) -> None:
        dialogue = DialogueManager(system_prompt="System message")
        dialogue.append_message("user", "Hello")

        messages = dialogue.build_messages_with_context(
            session_context="Topic: routing",
            tool_result="Current time: 12:00",
        )

        self.assertEqual(messages[0]["role"], "system")
        self.assertIn("System message", messages[0]["content"])
        self.assertIn("Topic: routing", messages[0]["content"])
        self.assertIn("Current time: 12:00", messages[0]["content"])
        self.assertEqual(sum(1 for message in messages if message["role"] == "system"), 1)


if __name__ == "__main__":
    unittest.main()
