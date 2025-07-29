"""
Tests for the parser module.
"""

import unittest
import tempfile
import pathlib
from trace_dev.parser import CodeParser, Symbol


class TestCodeParser(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures."""
        self.parser = CodeParser()
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = pathlib.Path(self.temp_dir)

    def test_python_parsing(self):
        """Test parsing Python code."""
        python_code = '''
import os
from typing import List

class TestClass:
    """A test class."""

    def __init__(self, name: str):
        self.name = name

    def get_name(self) -> str:
        """Get the name."""
        return self.name

def standalone_function(param1, param2):
    """A standalone function."""
    return param1 + param2

variable = "test"
'''

        # Write test file
        test_file = self.temp_path / "test.py"
        test_file.write_text(python_code)

        # Parse the file
        symbols = self.parser.parse_file(test_file, "python")

        # Check that we found symbols
        self.assertGreater(len(symbols), 0)

        # Check for specific symbols
        symbol_names = [s.name for s in symbols]
        symbol_types = [s.symbol_type for s in symbols]

        self.assertIn("os", symbol_names)
        self.assertIn("typing.List", symbol_names)
        self.assertIn("TestClass", symbol_names)
        self.assertIn("__init__", symbol_names)
        self.assertIn("get_name", symbol_names)
        self.assertIn("standalone_function", symbol_names)
        self.assertIn("variable", symbol_names)

        self.assertIn("import", symbol_types)
        self.assertIn("class", symbol_types)
        self.assertIn("function", symbol_types)
        self.assertIn("variable", symbol_types)

    def test_javascript_parsing(self):
        """Test parsing JavaScript code."""
        js_code = """
import React from 'react';
import { useState } from 'react';

class Component extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {
        return <div>Hello</div>;
    }
}

function myFunction(param1, param2) {
    return param1 + param2;
}

const arrowFunction = (x) => x * 2;

let variable = 42;
const constant = "test";
"""

        # Write test file
        test_file = self.temp_path / "test.js"
        test_file.write_text(js_code)

        # Parse the file
        symbols = self.parser.parse_file(test_file, "javascript")

        # Check that we found symbols
        self.assertGreater(len(symbols), 0)

        # Check for specific symbols
        symbol_names = [s.name for s in symbols]
        symbol_types = [s.symbol_type for s in symbols]

        self.assertIn("Component", symbol_names)
        self.assertIn("myFunction", symbol_names)
        self.assertIn("variable", symbol_names)
        self.assertIn("constant", symbol_names)

        self.assertIn("import", symbol_types)
        self.assertIn("class", symbol_types)
        self.assertIn("function", symbol_types)
        self.assertIn("variable", symbol_types)

    def test_unsupported_language(self):
        """Test handling of unsupported languages."""
        test_file = self.temp_path / "test.unknown"
        test_file.write_text("some content")

        symbols = self.parser.parse_file(test_file, "unknown_language")
        self.assertEqual(len(symbols), 0)

    def test_symbol_representation(self):
        """Test Symbol class methods."""
        symbol = Symbol(
            name="test_function",
            symbol_type="function",
            line_number=10,
            parameters=["param1", "param2"],
            docstring="A test function",
        )

        # Test string representation
        self.assertIn("test_function", str(symbol))
        self.assertIn("function", str(symbol))
        self.assertIn("10", str(symbol))

        # Test dictionary conversion
        symbol_dict = symbol.to_dict()
        self.assertEqual(symbol_dict["name"], "test_function")
        self.assertEqual(symbol_dict["type"], "function")
        self.assertEqual(symbol_dict["line"], 10)
        self.assertEqual(symbol_dict["parameters"], ["param1", "param2"])
        self.assertEqual(symbol_dict["docstring"], "A test function")

    def test_supported_languages(self):
        """Test getting supported languages."""
        supported = self.parser.get_supported_languages()
        self.assertIn("python", supported)
        self.assertIn("javascript", supported)
        self.assertIn("typescript", supported)

        self.assertTrue(self.parser.is_language_supported("python"))
        self.assertFalse(self.parser.is_language_supported("unknown"))


if __name__ == "__main__":
    unittest.main()
