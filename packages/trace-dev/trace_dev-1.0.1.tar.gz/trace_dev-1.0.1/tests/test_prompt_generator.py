"""
Tests for the prompt generator module.
"""

import unittest
import tempfile
import pathlib
from trace_dev.prompt_generator import PromptGenerator, PromptTemplate, DependencyGraph


class TestPromptGenerator(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = pathlib.Path(self.temp_dir)

        # Create test project structure
        (self.temp_path / "src").mkdir()
        (self.temp_path / "tests").mkdir()

        # Create test files
        (self.temp_path / "src" / "main.py").write_text(
            '''
import os
from utils import helper_function

class MainClass:
    """Main application class."""

    def __init__(self):
        self.name = "main"

    def run(self):
        """Run the application."""
        return helper_function()

def main():
    """Entry point."""
    app = MainClass()
    return app.run()
'''
        )

        (self.temp_path / "src" / "utils.py").write_text(
            '''
def helper_function():
    """A helper function."""
    return "Hello, World!"

class UtilityClass:
    """Utility class."""
    pass
'''
        )

        (self.temp_path / "README.md").write_text("# Test Project\n\nA test project.")
        (self.temp_path / "requirements.txt").write_text("requests>=2.0.0")

    def test_prompt_generation(self):
        """Test basic prompt generation."""
        generator = PromptGenerator(self.temp_dir)
        prompt = generator.generate_prompt("Add logging functionality")

        # Check that prompt contains expected sections
        self.assertIn("# Trace Development Prompt", prompt)
        self.assertIn("## Task Description", prompt)
        self.assertIn("Add logging functionality", prompt)
        self.assertIn("## Project Context", prompt)
        self.assertIn("## Trace Instructions", prompt)

        # Check project info
        self.assertIn("python", prompt.lower())
        self.assertIn("main.py", prompt)
        self.assertIn("utils.py", prompt)
        self.assertIn(
            "Has README**: Yes", prompt
        )  # README is detected but not listed in file structure

        # Check symbols
        self.assertIn("MainClass", prompt)
        self.assertIn("helper_function", prompt)
        self.assertIn("main", prompt)

    def test_template_rendering(self):
        """Test template rendering with custom context."""
        template = PromptTemplate()
        context = {
            "task_description": "Test task",
            "root_path": "/test/path",
            "total_files": 5,
            "languages": "python, javascript",
            "has_readme": "Yes",
            "config_files": "package.json",
            "file_structure": "src/\n  main.py",
            "language_breakdown": "Python: 2 files",
            "symbol_overview": "Functions: 3",
            "dependency_graph": "",
            "timestamp": "2024-01-01 12:00:00",
            "version": "0.1.0",
        }

        rendered = template.render(context)

        self.assertIn("Test task", rendered)
        self.assertIn("/test/path", rendered)
        self.assertIn("python, javascript", rendered)
        self.assertIn("Functions: 3", rendered)

    def test_dependency_graph(self):
        """Test dependency graph generation."""
        graph = DependencyGraph()
        graph.add_dependency("main.py", "utils.py")
        graph.add_dependency("main.py", "config.py")
        graph.add_dependency("utils.py", "helpers.py")

        mermaid = graph.generate_mermaid()

        self.assertIn("graph LR", mermaid)
        self.assertIn("main.py", mermaid)
        self.assertIn("utils.py", mermaid)
        self.assertIn("-->", mermaid)

    def test_custom_template(self):
        """Test using a custom template."""
        custom_template = PromptTemplate(
            "Task: {task_description}\nFiles: {total_files}"
        )
        generator = PromptGenerator(self.temp_dir, template=custom_template)

        prompt = generator.generate_prompt("Custom task")

        self.assertIn("Task: Custom task", prompt)
        self.assertIn("Files:", prompt)
        self.assertNotIn("# Trace Development Prompt", prompt)

    def test_no_graph_option(self):
        """Test disabling dependency graph generation."""
        generator = PromptGenerator(self.temp_dir, include_graph=False)
        prompt = generator.generate_prompt("Test task")

        # Should not contain mermaid graph
        self.assertNotIn("```mermaid", prompt)
        self.assertNotIn("## Dependency Graph", prompt)

    def test_empty_project(self):
        """Test handling of empty project."""
        empty_dir = tempfile.mkdtemp()
        generator = PromptGenerator(empty_dir)
        prompt = generator.generate_prompt("Test empty project")

        self.assertIn("Test empty project", prompt)
        self.assertIn("**Total Files**: 0", prompt)
        self.assertIn("No symbols found", prompt)


if __name__ == "__main__":
    unittest.main()
