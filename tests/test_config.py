import unittest

from jarvis.config import _extract_legacy_assignment


class ConfigParsingTest(unittest.TestCase):
    def test_extracts_legacy_assignment_default_when_missing(self) -> None:
        self.assertEqual(_extract_legacy_assignment("THIS_KEY_DOES_NOT_EXIST", "x"), "x")


if __name__ == "__main__":
    unittest.main()
