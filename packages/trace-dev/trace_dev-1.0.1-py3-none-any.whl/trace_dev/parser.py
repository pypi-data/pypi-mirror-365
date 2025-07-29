"""
Tree-sitter parser module for trace-dev CLI.
Handles AST parsing and symbol extraction from source code files.
"""

from tree_sitter import Language, Parser
import tree_sitter_python
import tree_sitter_javascript
import tree_sitter_typescript
from typing import Dict, List, Set, Any, Optional
import pathlib


class Symbol:
    """Represents a code symbol (function, class, import, etc.)."""

    def __init__(
        self,
        name: str,
        symbol_type: str,
        line_number: int,
        column: int = 0,
        end_line: Optional[int] = None,
        parameters: Optional[List[str]] = None,
        return_type: Optional[str] = None,
        docstring: Optional[str] = None,
        modifiers: Optional[List[str]] = None,
    ):
        self.name = name
        self.symbol_type = (
            symbol_type  # 'function', 'class', 'import', 'variable', etc.
        )
        self.line_number = line_number
        self.column = column
        self.end_line = end_line
        self.parameters = parameters or []
        self.return_type = return_type
        self.docstring = docstring
        self.modifiers = modifiers or []

    def __repr__(self):
        return f"Symbol(name='{self.name}', type='{self.symbol_type}', line={self.line_number})"

    def to_dict(self) -> Dict[str, Any]:
        """Convert symbol to dictionary representation."""
        return {
            "name": self.name,
            "type": self.symbol_type,
            "line": self.line_number,
            "column": self.column,
            "end_line": self.end_line,
            "parameters": self.parameters,
            "return_type": self.return_type,
            "docstring": self.docstring,
            "modifiers": self.modifiers,
        }


class LanguageParser:
    """Base class for language-specific parsers."""

    def __init__(self, language: Language):
        self.language = language
        self.parser = Parser()
        self.parser.language = language

    def parse_file(self, file_path: pathlib.Path) -> List[Symbol]:
        """Parse a file and extract symbols."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source_code = f.read()
            return self.parse_source(source_code)
        except (UnicodeDecodeError, OSError) as e:
            print(f"Warning: Could not parse {file_path}: {e}")
            return []

    def parse_source(self, source_code: str) -> List[Symbol]:
        """Parse source code and extract symbols."""
        tree = self.parser.parse(bytes(source_code, "utf8"))
        return self.extract_symbols(tree.root_node, source_code)

    def extract_symbols(self, node, source_code: str) -> List[Symbol]:
        """Extract symbols from AST node. Override in subclasses."""
        raise NotImplementedError("Subclasses must implement extract_symbols")

    def get_node_text(self, node, source_code: str) -> str:
        """Get text content of a node."""
        return source_code[node.start_byte : node.end_byte]

    def get_line_number(self, node) -> int:
        """Get line number of a node (1-based)."""
        return node.start_point[0] + 1


class PythonParser(LanguageParser):
    """Parser for Python source code."""

    def __init__(self):
        super().__init__(Language(tree_sitter_python.language()))

    def extract_symbols(self, node, source_code: str) -> List[Symbol]:
        """Extract symbols from Python AST."""
        symbols = []

        def traverse(node):
            if node.type == "function_definition":
                symbols.append(self._extract_function(node, source_code))
            elif node.type == "class_definition":
                symbols.append(self._extract_class(node, source_code))
            elif (
                node.type == "import_statement" or node.type == "import_from_statement"
            ):
                symbols.extend(self._extract_imports(node, source_code))
            elif node.type == "assignment":
                symbols.extend(self._extract_variables(node, source_code))

            for child in node.children:
                traverse(child)

        traverse(node)
        return symbols

    def _extract_function(self, node, source_code: str) -> Symbol:
        """Extract function definition."""
        name_node = node.child_by_field_name("name")
        name = self.get_node_text(name_node, source_code) if name_node else "unknown"

        # Extract parameters
        parameters = []
        params_node = node.child_by_field_name("parameters")
        if params_node:
            for param in params_node.children:
                if param.type == "identifier":
                    parameters.append(self.get_node_text(param, source_code))
                elif param.type == "typed_parameter":
                    param_name = param.child_by_field_name("pattern")
                    if param_name:
                        parameters.append(self.get_node_text(param_name, source_code))

        # Extract docstring
        docstring = None
        body = node.child_by_field_name("body")
        if body and body.children:
            first_stmt = body.children[0]
            if first_stmt.type == "expression_statement":
                expr = first_stmt.children[0]
                if expr.type == "string":
                    docstring = self.get_node_text(expr, source_code).strip("\"'")

        return Symbol(
            name=name,
            symbol_type="function",
            line_number=self.get_line_number(node),
            end_line=node.end_point[0] + 1,
            parameters=parameters,
            docstring=docstring or "",
        )

    def _extract_class(self, node, source_code: str) -> Symbol:
        """Extract class definition."""
        name_node = node.child_by_field_name("name")
        name = self.get_node_text(name_node, source_code) if name_node else "unknown"

        # Extract base classes
        superclasses = []
        superclasses_node = node.child_by_field_name("superclasses")
        if superclasses_node:
            for child in superclasses_node.children:
                if child.type == "identifier":
                    superclasses.append(self.get_node_text(child, source_code))

        return Symbol(
            name=name,
            symbol_type="class",
            line_number=self.get_line_number(node),
            end_line=node.end_point[0] + 1,
            parameters=superclasses,  # Use parameters field for base classes
        )

    def _extract_imports(self, node, source_code: str) -> List[Symbol]:
        """Extract import statements."""
        symbols = []

        if node.type == "import_statement":
            # import module
            for child in node.children:
                if child.type == "dotted_name" or child.type == "identifier":
                    module_name = self.get_node_text(child, source_code)
                    symbols.append(
                        Symbol(
                            name=module_name,
                            symbol_type="import",
                            line_number=self.get_line_number(node),
                        )
                    )
        elif node.type == "import_from_statement":
            # from module import name
            module_node = None
            import_names = []

            for child in node.children:
                if child.type == "dotted_name" and module_node is None:
                    # This is the module name (first dotted_name after 'from')
                    module_node = child
                elif child.type == "dotted_name" and module_node is not None:
                    # This is an imported name
                    import_names.append(self.get_node_text(child, source_code))
                elif child.type == "identifier" and module_node is not None:
                    # This is also an imported name
                    import_names.append(self.get_node_text(child, source_code))

            module_name = (
                self.get_node_text(module_node, source_code) if module_node else ""
            )

            for import_name in import_names:
                full_name = (
                    f"{module_name}.{import_name}" if module_name else import_name
                )
                symbols.append(
                    Symbol(
                        name=full_name,
                        symbol_type="import",
                        line_number=self.get_line_number(node),
                    )
                )

        return symbols

    def _extract_variables(self, node, source_code: str) -> List[Symbol]:
        """Extract variable assignments."""
        symbols = []

        # Simple variable assignment
        left = node.child_by_field_name("left")
        if left and left.type == "identifier":
            var_name = self.get_node_text(left, source_code)
            symbols.append(
                Symbol(
                    name=var_name,
                    symbol_type="variable",
                    line_number=self.get_line_number(node),
                )
            )

        return symbols


class JavaScriptParser(LanguageParser):
    """Parser for JavaScript/TypeScript source code."""

    def __init__(self, is_typescript=False):
        if is_typescript:
            super().__init__(Language(tree_sitter_typescript.language_typescript()))
        else:
            super().__init__(Language(tree_sitter_javascript.language()))

    def extract_symbols(self, node, source_code: str) -> List[Symbol]:
        """Extract symbols from JavaScript/TypeScript AST."""
        symbols = []

        def traverse(node):
            if node.type in [
                "function_declaration",
                "function_expression",
                "arrow_function",
            ]:
                symbols.append(self._extract_function(node, source_code))
            elif node.type == "class_declaration":
                symbols.append(self._extract_class(node, source_code))
            elif node.type == "import_statement":
                symbols.extend(self._extract_imports(node, source_code))
            elif node.type in ["variable_declaration", "lexical_declaration"]:
                symbols.extend(self._extract_variables(node, source_code))

            for child in node.children:
                traverse(child)

        traverse(node)
        return symbols

    def _extract_function(self, node, source_code: str) -> Symbol:
        """Extract function definition."""
        name = "anonymous"

        # Try to get function name
        if node.type == "function_declaration":
            name_node = node.child_by_field_name("name")
            if name_node:
                name = self.get_node_text(name_node, source_code)

        # Extract parameters
        parameters = []
        params_node = node.child_by_field_name("parameters")
        if params_node:
            for param in params_node.children:
                if param.type == "identifier":
                    parameters.append(self.get_node_text(param, source_code))
                elif param.type == "required_parameter":
                    param_name = param.child_by_field_name("pattern")
                    if param_name:
                        parameters.append(self.get_node_text(param_name, source_code))

        return Symbol(
            name=name,
            symbol_type="function",
            line_number=self.get_line_number(node),
            end_line=node.end_point[0] + 1,
            parameters=parameters,
        )

    def _extract_class(self, node, source_code: str) -> Symbol:
        """Extract class definition."""
        name_node = node.child_by_field_name("name")
        name = self.get_node_text(name_node, source_code) if name_node else "unknown"

        return Symbol(
            name=name,
            symbol_type="class",
            line_number=self.get_line_number(node),
            end_line=node.end_point[0] + 1,
        )

    def _extract_imports(self, node, source_code: str) -> List[Symbol]:
        """Extract import statements."""
        symbols = []

        # Get the module name
        source_node = node.child_by_field_name("source")
        if source_node:
            module_name = self.get_node_text(source_node, source_code).strip("\"'")
            symbols.append(
                Symbol(
                    name=module_name,
                    symbol_type="import",
                    line_number=self.get_line_number(node),
                )
            )

        return symbols

    def _extract_variables(self, node, source_code: str) -> List[Symbol]:
        """Extract variable declarations."""
        symbols = []

        for child in node.children:
            if child.type == "variable_declarator":
                name_node = child.child_by_field_name("name")
                if name_node and name_node.type == "identifier":
                    var_name = self.get_node_text(name_node, source_code)
                    symbols.append(
                        Symbol(
                            name=var_name,
                            symbol_type="variable",
                            line_number=self.get_line_number(child),
                        )
                    )

        return symbols


class CodeParser:
    """Main parser that handles multiple languages."""

    def __init__(self):
        self.parsers = {
            "python": PythonParser(),
            "javascript": JavaScriptParser(is_typescript=False),
            "typescript": JavaScriptParser(is_typescript=True),
            # Add more parsers as needed
        }

    def parse_file(self, file_path: pathlib.Path, language: str) -> List[Symbol]:
        """Parse a file and extract symbols."""
        if language not in self.parsers:
            print(f"Warning: No parser available for language '{language}'")
            return []

        parser = self.parsers[language]
        return parser.parse_file(file_path)

    def get_supported_languages(self) -> Set[str]:
        """Get set of supported languages."""
        return set(self.parsers.keys())

    def is_language_supported(self, language: str) -> bool:
        """Check if a language is supported."""
        return language in self.parsers
