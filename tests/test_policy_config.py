import tempfile
import unittest
from pathlib import Path

from src.config.policy import load_policy_text, resolve_policy_path


class PolicyConfigTests(unittest.TestCase):
    def test_default_policy_is_public_safe_sample(self):
        policy_text = load_policy_text()

        self.assertIn("Reference Decision Policy", policy_text)
        self.assertIn("public-safe", policy_text)

    def test_resolve_policy_path_accepts_relative_paths(self):
        path = resolve_policy_path("config/reference_policy.md")

        self.assertTrue(path.is_absolute())
        self.assertEqual(path.name, "reference_policy.md")

    def test_load_policy_text_rejects_empty_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            policy_path = Path(temp_dir) / "empty.md"
            policy_path.write_text("  \n", encoding="utf-8")

            with self.assertRaises(ValueError):
                load_policy_text(policy_path)

    def test_load_policy_text_rejects_missing_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaises(FileNotFoundError):
                load_policy_text(Path(temp_dir) / "missing.md")


if __name__ == "__main__":
    unittest.main()
