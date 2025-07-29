"""
Integration tests for trace-dev CLI.
"""

import unittest
import tempfile
import pathlib
import subprocess
import time


class TestCLIIntegration(unittest.TestCase):

    @classmethod
    def get_cli_command(cls):
        """Get the path to the trace-dev CLI command."""
        # Get the path to the virtual environment's trace-dev binary
        project_root = pathlib.Path(__file__).parent.parent
        venv_bin = project_root / "venv" / "bin" / "trace-dev"
        if venv_bin.exists():
            return str(venv_bin)

        # Try Python -m approach for CI environments
        try:
            import subprocess

            result = subprocess.run(
                ["python", "-m", "trace_dev.cli", "--help"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                return "python -m trace_dev.cli"
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            pass

        # Fallback for CI environments or different setups
        return "trace-dev"

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = pathlib.Path(self.temp_dir)
        self.cli_cmd = self.get_cli_command()

        # Create a realistic test project structure
        (self.temp_path / "src").mkdir()
        (self.temp_path / "src" / "main").mkdir()
        (self.temp_path / "src" / "utils").mkdir()
        (self.temp_path / "tests").mkdir()
        (self.temp_path / "docs").mkdir()

        # Create multiple Python files
        for i in range(10):
            (self.temp_path / "src" / "main" / f"module_{i}.py").write_text(
                f'''
import os
import sys
from utils.helper import helper_function

class Module{i}:
    """Module {i} class."""

    def __init__(self):
        self.name = "module_{i}"

    def process(self, data):
        """Process data."""
        return helper_function(data)

    def validate(self, input_data):
        """Validate input."""
        if not input_data:
            raise ValueError("Invalid input")
        return True

def main():
    """Main function for module {i}."""
    module = Module{i}()
    return module.process("test_data")

if __name__ == "__main__":
    main()
'''
            )

        # Create utility files
        (self.temp_path / "src" / "utils" / "__init__.py").write_text("")
        (self.temp_path / "src" / "utils" / "helper.py").write_text(
            '''
import json
import logging

def helper_function(data):
    """Helper function for processing data."""
    logging.info(f"Processing: {data}")
    return json.dumps({"processed": data})

def validate_config(config):
    """Validate configuration."""
    required_keys = ['name', 'version']
    for key in required_keys:
        if key not in config:
            raise KeyError(f"Missing required key: {key}")
    return True

class ConfigManager:
    """Configuration manager."""

    def __init__(self, config_path):
        self.config_path = config_path
        self.config = {}

    def load(self):
        """Load configuration."""
        with open(self.config_path, 'r') as f:
            self.config = json.load(f)
        return self.config
'''
        )

        # Create test files
        (self.temp_path / "tests" / "test_main.py").write_text(
            '''
import unittest
from src.main.module_0 import Module0

class TestModule0(unittest.TestCase):

    def test_process(self):
        """Test processing."""
        module = Module0()
        result = module.process("test")
        self.assertIsNotNone(result)

if __name__ == "__main__":
    unittest.main()
'''
        )

        # Create README and config files
        (self.temp_path / "README.md").write_text(
            "# Test Project\n\nA test project for trace-dev."
        )
        (self.temp_path / "requirements.txt").write_text(
            "requests>=2.0.0\nnumpy>=1.20.0"
        )
        (self.temp_path / "setup.py").write_text(
            'from setuptools import setup\nsetup(name="test-project")'
        )

    def test_cli_generate_command(self):
        """Test the CLI generate command."""
        # Run trace-dev generate command
        result = subprocess.run(
            [
                self.cli_cmd,
                "generate",
                "Add error handling and logging",
                "--root",
                str(self.temp_path),
                "--verbose",
            ],
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("# Trace Development Prompt", result.stdout)
        self.assertIn("Add error handling and logging", result.stdout)
        self.assertIn("python", result.stdout.lower())
        # Module0 should appear somewhere in the output (file name or class name)
        self.assertTrue("Module0" in result.stdout or "module_0.py" in result.stdout)
        self.assertIn("helper_function", result.stdout)

    def test_cli_info_command(self):
        """Test the CLI info command."""
        result = subprocess.run(
            [self.cli_cmd, "info", "--root", str(self.temp_path)],
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("Project Analysis:", result.stdout)
        self.assertIn("Total Files:", result.stdout)
        self.assertIn("Python:", result.stdout)
        self.assertIn("Functions:", result.stdout)

    def test_cli_output_to_file(self):
        """Test outputting to a file."""
        output_file = self.temp_path / "trace_output.md"

        result = subprocess.run(
            [
                self.cli_cmd,
                "generate",
                "Implement caching",
                "--root",
                str(self.temp_path),
                "--output",
                str(output_file),
            ],
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0)
        self.assertTrue(output_file.exists())

        content = output_file.read_text()
        self.assertIn("# Trace Development Prompt", content)
        self.assertIn("Implement caching", content)

    def test_cli_config_generation(self):
        """Test configuration file generation."""
        config_file = self.temp_path / "test-config.yaml"

        result = subprocess.run(
            [self.cli_cmd, "init-config", "--output", str(config_file)],
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0)
        self.assertTrue(config_file.exists())

        content = config_file.read_text()
        self.assertIn("scan_dirs:", content)
        self.assertIn("language_map:", content)
        self.assertIn("include_graph:", content)

    def test_performance_requirements(self):
        """Test that scanning meets performance requirements (< 2 seconds for 1000 files)."""
        # The PRD specifies scanning up to 1000 files under 2 seconds
        # Our test project has about 13 files, so it should be very fast

        start_time = time.time()

        result = subprocess.run(
            [self.cli_cmd, "info", "--root", str(self.temp_path)],
            capture_output=True,
            text=True,
        )

        end_time = time.time()
        execution_time = end_time - start_time

        self.assertEqual(result.returncode, 0)
        self.assertLess(
            execution_time,
            2.0,
            f"Execution took {execution_time:.2f} seconds, should be < 2.0",
        )

        # For our small test project, it should be much faster
        self.assertLess(
            execution_time,
            0.5,
            f"Small project took {execution_time:.2f} seconds, should be < 0.5",
        )

    def test_error_handling(self):
        """Test error handling for invalid inputs."""
        # Test with non-existent directory
        result = subprocess.run(
            [self.cli_cmd, "generate", "Test task", "--root", "/non/existent/path"],
            capture_output=True,
            text=True,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Error:", result.stderr)

    def test_no_graph_option(self):
        """Test the --no-graph option."""
        result = subprocess.run(
            [
                self.cli_cmd,
                "generate",
                "Test task",
                "--root",
                str(self.temp_path),
                "--no-graph",
            ],
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0)
        # Should not contain mermaid graph
        self.assertNotIn("```mermaid", result.stdout)
        self.assertNotIn("## Dependency Graph", result.stdout)

    def test_custom_scan_dirs(self):
        """Test custom scan directories."""
        result = subprocess.run(
            [
                self.cli_cmd,
                "generate",
                "Test task",
                "--root",
                str(self.temp_path),
                "--scan-dirs",
                "tests",
            ],
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0)
        # Should find test files but not src files
        self.assertIn("test_main.py", result.stdout)
        self.assertNotIn("module_0.py", result.stdout)


class TestEndToEndWorkflow(unittest.TestCase):
    """Test complete end-to-end workflows."""

    @classmethod
    def get_cli_command(cls):
        """Get the path to the trace-dev CLI command."""
        # Get the path to the virtual environment's trace-dev binary
        project_root = pathlib.Path(__file__).parent.parent
        venv_bin = project_root / "venv" / "bin" / "trace-dev"
        if venv_bin.exists():
            return str(venv_bin)

        # Try installed package approach for CI environments
        try:
            import subprocess

            result = subprocess.run(
                ["trace-dev", "--help"], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                return "trace-dev"
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            pass

        # Fallback for CI environments or different setups
        return "trace-dev"

    def setUp(self):
        """Set up test fixtures."""
        self.cli_cmd = self.get_cli_command()

    def test_complete_workflow(self):
        """Test a complete workflow from project analysis to prompt generation."""
        temp_dir = tempfile.mkdtemp()
        temp_path = pathlib.Path(temp_dir)

        # Create a simple project
        (temp_path / "src").mkdir()
        (temp_path / "src" / "app.py").write_text(
            """
from utils import database

class Application:
    def __init__(self):
        self.db = database.connect()

    def run(self):
        return "Running application"
"""
        )

        (temp_path / "src" / "utils.py").write_text(
            """
class Database:
    def connect(self):
        return "Connected"

database = Database()
"""
        )

        # Step 1: Analyze project
        info_result = subprocess.run(
            [self.cli_cmd, "info", "--root", str(temp_path)],
            capture_output=True,
            text=True,
        )

        self.assertEqual(info_result.returncode, 0)
        self.assertIn("Python: 2 files", info_result.stdout)

        # Step 2: Generate configuration
        config_file = temp_path / "trace-dev.yaml"
        config_result = subprocess.run(
            [self.cli_cmd, "init-config", "--output", str(config_file)],
            capture_output=True,
            text=True,
        )

        self.assertEqual(config_result.returncode, 0)
        self.assertTrue(config_file.exists())

        # Step 3: Generate trace prompt
        output_file = temp_path / "trace.md"
        generate_result = subprocess.run(
            [
                self.cli_cmd,
                "generate",
                "Add database connection pooling",
                "--root",
                str(temp_path),
                "--config",
                str(config_file),
                "--output",
                str(output_file),
            ],
            capture_output=True,
            text=True,
        )

        self.assertEqual(generate_result.returncode, 0)
        self.assertTrue(output_file.exists())

        # Verify the generated prompt
        prompt_content = output_file.read_text()
        self.assertIn("Add database connection pooling", prompt_content)
        self.assertIn("Application", prompt_content)
        self.assertIn("Database", prompt_content)
        # Check for the custom template's section header instead of default template
        self.assertIn("## Development Guidelines", prompt_content)


if __name__ == "__main__":
    unittest.main()
