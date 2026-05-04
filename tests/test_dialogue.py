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


if __name__ == "__main__":
    unittest.main()
