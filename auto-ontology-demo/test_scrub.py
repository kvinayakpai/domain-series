"""python3 -m unittest auto-ontology-demo/test_scrub.py   (or run from this folder)"""
import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import scrub  # noqa: E402


class ScrubTest(unittest.TestCase):
    def test_nvidia_key(self):
        self.assertNotIn("nvapi-abcdefgh12345", scrub.clean("key nvapi-abcdefgh12345 used"))

    def test_bearer_header(self):
        out = scrub.clean("Authorization: Bearer abc.DEF-123_xyz~+/== sent")
        self.assertNotIn("abc.DEF", out)
        self.assertIn("Bearer [redacted]", out)

    def test_json_token_field(self):
        out = scrub.clean('{"api_key": "sk-1234567890abcdef", "name": "keep"}')
        self.assertNotIn("1234567890abcdef", out)
        self.assertIn('"name": "keep"', out)

    def test_assignment(self):
        out = scrub.clean("PASSWORD=hunter2hunter2hunter2 next")
        self.assertNotIn("hunter2", out)

    def test_scrub_env_and_short_values_kept(self):
        os.environ["SCRUB"] = "throwaway-pass-1"
        try:
            self.assertEqual(scrub.clean("pw throwaway-pass-1"), "pw [redacted]")
        finally:
            del os.environ["SCRUB"]
        self.assertEqual(scrub.clean("token: short"), "token: short")


if __name__ == "__main__":
    unittest.main()
