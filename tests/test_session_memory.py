import unittest

from jarvis.session_memory import SessionMemory


class SessionMemoryTest(unittest.TestCase):
    def test_extracts_active_facts(self) -> None:
        memory = SessionMemory(summary_interval=2, recent_turn_limit=2)

        memory.update("My name is Alex and I prefer short replies.", "Noted.")

        context = memory.build_context_block()
        self.assertIn("my name is alex and i prefer short replies", context)

    def test_builds_summary_after_interval(self) -> None:
        memory = SessionMemory(summary_interval=2, recent_turn_limit=1)

        memory.update("First user turn", "First assistant turn")
        memory.update("Second user turn", "Second assistant turn")

        self.assertIn("First user turn", memory.summary)

    def test_summary_accumulates_older_context(self) -> None:
        memory = SessionMemory(summary_interval=2, recent_turn_limit=1)

        memory.update("Turn 1", "Reply 1")
        memory.update("Turn 2", "Reply 2")
        memory.update("Turn 3", "Reply 3")
        memory.update("Turn 4", "Reply 4")

        self.assertIn("Turn 1", memory.summary)
        self.assertIn("Turn 2", memory.summary)

    def test_answered_question_is_removed_from_open_loops(self) -> None:
        memory = SessionMemory(summary_interval=2, recent_turn_limit=2)

        memory.update("What time is it?", "It is noon.")

        self.assertEqual(memory.open_loops, [])


if __name__ == "__main__":
    unittest.main()
