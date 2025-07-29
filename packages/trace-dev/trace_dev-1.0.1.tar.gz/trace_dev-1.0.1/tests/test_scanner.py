"""
Tests for the file scanner module.
"""

import unittest
import tempfile
import pathlib
from trace_dev.scanner import FileScanner


class TestFileScanner(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = pathlib.Path(self.temp_dir)

        # Create test directory structure
        (self.temp_path / "src").mkdir()
        (self.temp_path / "tests").mkdir()
        (self.temp_path / "node_modules").mkdir()

        # Create test files
        (self.temp_path / "src" / "main.py").write_text('print("hello")')
        (self.temp_path / "src" / "utils.js").write_text('console.log("hello")')
        (self.temp_path / "tests" / "test_main.py").write_text("import unittest")
        (self.temp_path / "README.md").write_text("# Test Project")
        (self.temp_path / "package.json").write_text("{}")
        (self.temp_path / "node_modules" / "lib.js").write_text("// library")

    def test_language_detection(self):
        """Test language detection by file extension."""
        scanner = FileScanner(self.temp_dir)

        test_cases = [
            ("test.py", "python"),
            ("test.js", "javascript"),
            ("test.ts", "typescript"),
            ("test.go", "go"),
            ("test.rs", "rust"),
            ("test.unknown", None),
        ]

        for filename, expected_lang in test_cases:
            file_path = pathlib.Path(filename)
            self.assertEqual(scanner.detect_language(file_path), expected_lang)

    def test_ignore_patterns(self):
        """Test that ignore patterns work correctly."""
        scanner = FileScanner(self.temp_dir)

        # node_modules should be ignored
        node_modules_file = self.temp_path / "node_modules" / "lib.js"
        self.assertTrue(scanner.should_ignore(node_modules_file))

        # src files should not be ignored
        src_file = self.temp_path / "src" / "main.py"
        self.assertFalse(scanner.should_ignore(src_file))

    def test_scan_files(self):
        """Test scanning for source files."""
        scanner = FileScanner(self.temp_dir)
        files_by_language = scanner.scan()

        # Should find Python and JavaScript files
        self.assertIn("python", files_by_language)
        self.assertIn("javascript", files_by_language)

        # Should not include node_modules files
        js_files = files_by_language["javascript"]
        js_filenames = [f.name for f in js_files]
        self.assertIn("utils.js", js_filenames)
        self.assertNotIn("lib.js", js_filenames)

    def test_project_info(self):
        """Test project information gathering."""
        scanner = FileScanner(self.temp_dir)
        info = scanner.get_project_info()

        self.assertTrue(info["has_readme"])
        self.assertIn("README.md", info["readme_files"])
        self.assertIn("package.json", info["config_files"])
        self.assertGreater(info["total_files"], 0)
        self.assertIn("python", info["languages"])
        self.assertIn("javascript", info["languages"])


if __name__ == "__main__":
    unittest.main()
