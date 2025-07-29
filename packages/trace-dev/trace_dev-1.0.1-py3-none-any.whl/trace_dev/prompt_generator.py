"""
Prompt generator module for trace-dev CLI.
Handles generation of standardized trace prompts for AI-driven development workflows.
"""

from typing import Dict, List, Optional, Any
import pathlib
from datetime import datetime
from .scanner import FileScanner
from .parser import CodeParser, Symbol


class DependencyGraph:
    """Generates dependency graphs for project files."""

    def __init__(self):
        self.dependencies = {}  # file -> set of dependencies

    def add_dependency(self, source_file: str, dependency: str):
        """Add a dependency relationship."""
        if source_file not in self.dependencies:
            self.dependencies[source_file] = set()
        self.dependencies[source_file].add(dependency)

    def analyze_imports(
        self,
        files_by_language: Dict[str, List[pathlib.Path]],
        symbols_by_file: Dict[str, List[Symbol]],
    ):
        """Analyze import statements to build dependency graph."""
        # Create a mapping of module names to files
        module_to_file = {}

        for language, files in files_by_language.items():
            for file_path in files:
                # Use relative path as module identifier
                relative_path = str(file_path).replace("/", ".").replace("\\", ".")
                if relative_path.endswith(".py"):
                    module_name = relative_path[:-3]  # Remove .py extension
                elif relative_path.endswith(".js"):
                    module_name = relative_path[:-3]  # Remove .js extension
                else:
                    module_name = relative_path

                module_to_file[module_name] = str(file_path)

        # Analyze imports to find dependencies
        for file_path_str, symbols in symbols_by_file.items():
            for symbol in symbols:
                if symbol.symbol_type == "import":
                    # Try to match import to a local file
                    import_name = symbol.name

                    # Check if this import refers to a local file
                    for module_name, target_file in module_to_file.items():
                        if (
                            import_name in module_name
                            or module_name in import_name
                            or import_name.split(".")[0] in module_name
                        ):
                            self.add_dependency(file_path_str, target_file)
                            break

    def generate_mermaid(self) -> str:
        """Generate a mermaid graph representation of dependencies."""
        if not self.dependencies:
            return ""

        lines = ["graph LR"]

        # Create node definitions with clean names
        node_map = {}
        node_counter = 1

        all_files = set()
        for source, deps in self.dependencies.items():
            all_files.add(source)
            all_files.update(deps)

        for file_path in all_files:
            # Create a clean node name
            file_name = pathlib.Path(file_path).name
            node_name = f"N{node_counter}"
            node_map[file_path] = node_name
            lines.append(f'  {node_name}["{file_name}"]')
            node_counter += 1

        # Add dependency relationships
        for source, deps in self.dependencies.items():
            source_node = node_map[source]
            for dep in deps:
                if dep in node_map:
                    dep_node = node_map[dep]
                    lines.append(f"  {source_node} --> {dep_node}")

        return "\n".join(lines)


class PromptTemplate:
    """Template for generating trace prompts."""

    DEFAULT_TEMPLATE = """# Trace Development Prompt

## Task Description
{task_description}

## Project Context

### Project Overview
- **Root Path**: {root_path}
- **Total Files**: {total_files}
- **Languages Detected**: {languages}
- **Has README**: {has_readme}
- **Configuration Files**: {config_files}

### File Structure
{file_structure}

### Language Breakdown
{language_breakdown}

### Symbol Overview
{symbol_overview}

{dependency_graph}

## Trace Instructions

When implementing the requested task, please follow these guidelines:

1. **Document Assumptions**: Clearly state any assumptions you make about the codebase,
   requirements, or implementation approach.

2. **Explain Dependencies**: Identify and explain any dependencies between components,
   modules, or functions that are relevant to your implementation.

3. **Trace Logic Path**: Provide a step-by-step explanation of your reasoning and implementation approach, including:
   - Why you chose specific approaches or patterns
   - How your changes integrate with existing code
   - What potential side effects or considerations exist

4. **Consider Context**: Take into account the existing codebase structure, patterns,
   and conventions when implementing changes.

5. **Validate Approach**: Before implementing, explain how you would test or validate your solution.

## Additional Context
- Generated on: {timestamp}
- Tool: trace-dev v{version}
"""

    def __init__(self, template: Optional[str] = None):
        self.template = template or self.DEFAULT_TEMPLATE

    def render(self, context: Dict[str, Any]) -> str:
        """Render the template with the provided context."""
        return self.template.format(**context)


class PromptGenerator:
    """Main prompt generator that combines scanning, parsing, and templating."""

    def __init__(
        self,
        root_path: str = ".",
        template: Optional[PromptTemplate] = None,
        include_graph: bool = True,
    ):
        self.root_path = pathlib.Path(root_path).resolve()
        self.scanner = FileScanner(root_path)
        self.parser = CodeParser()
        self.template = template or PromptTemplate()
        self.include_graph = include_graph

    def generate_prompt(self, task_description: str) -> str:
        """Generate a complete trace prompt for the given task."""
        # Scan for files
        files_by_language = self.scanner.scan()
        project_info = self.scanner.get_project_info()

        # Parse files and extract symbols
        symbols_by_file = {}
        all_symbols = []

        for language, files in files_by_language.items():
            if self.parser.is_language_supported(language):
                for file_path in files:
                    symbols = self.parser.parse_file(file_path, language)
                    file_key = str(file_path.relative_to(self.root_path))
                    symbols_by_file[file_key] = symbols
                    all_symbols.extend(symbols)

        # Generate dependency graph
        dependency_graph = DependencyGraph()
        dependency_graph.analyze_imports(files_by_language, symbols_by_file)

        # Build context for template
        context = {
            "task_description": task_description,
            "root_path": str(self.root_path),
            "total_files": project_info["total_files"],
            "languages": ", ".join(sorted(project_info["languages"])),
            "has_readme": "Yes" if project_info["has_readme"] else "No",
            "config_files": (
                ", ".join(project_info["config_files"])
                if project_info["config_files"]
                else "None"
            ),
            "file_structure": self._generate_file_structure(files_by_language),
            "language_breakdown": self._generate_language_breakdown(
                files_by_language, symbols_by_file
            ),
            "symbol_overview": self._generate_symbol_overview(all_symbols),
            "dependency_graph": (
                self._generate_dependency_section(dependency_graph)
                if self.include_graph
                else ""
            ),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "0.1.0",
        }

        return self.template.render(context)

    def _generate_file_structure(
        self, files_by_language: Dict[str, List[pathlib.Path]]
    ) -> str:
        """Generate a file structure overview."""
        lines = []

        all_files = []
        for files in files_by_language.values():
            all_files.extend(files)

        # Group by directory
        dirs: Dict[str, List[str]] = {}
        for file_path in all_files:
            relative_path = file_path.relative_to(self.root_path)
            dir_path = relative_path.parent
            if str(dir_path) not in dirs:
                dirs[str(dir_path)] = []
            dirs[str(dir_path)].append(relative_path.name)

        for dir_path_str in sorted(dirs.keys()):
            if dir_path_str == ".":
                lines.append("**Root Directory:**")
            else:
                lines.append(f"**{dir_path_str}/**")

            for file_name in sorted(dirs[dir_path_str]):
                lines.append(f"  - {file_name}")
            lines.append("")

        return "\n".join(lines)

    def _generate_language_breakdown(
        self,
        files_by_language: Dict[str, List[pathlib.Path]],
        symbols_by_file: Dict[str, List[Symbol]],
    ) -> str:
        """Generate language-specific breakdown."""
        lines = []

        for language in sorted(files_by_language.keys()):
            files = files_by_language[language]
            lines.append(f"**{language.title()}** ({len(files)} files)")

            for file_path in files:
                relative_path = file_path.relative_to(self.root_path)
                file_key = str(relative_path)

                lines.append(f"  - `{relative_path}`")

                # Add symbol summary for this file
                if file_key in symbols_by_file:
                    symbols = symbols_by_file[file_key]
                    symbol_counts: Dict[str, int] = {}
                    for symbol in symbols:
                        symbol_counts[symbol.symbol_type] = (
                            symbol_counts.get(symbol.symbol_type, 0) + 1
                        )

                    if symbol_counts:
                        summary_parts = []
                        for symbol_type, count in sorted(symbol_counts.items()):
                            summary_parts.append(
                                f"{count} {symbol_type}{'s' if count != 1 else ''}"
                            )
                        lines.append(f"    - {', '.join(summary_parts)}")

            lines.append("")

        return "\n".join(lines)

    def _generate_symbol_overview(self, symbols: List[Symbol]) -> str:
        """Generate an overview of all symbols found."""
        if not symbols:
            return "No symbols found."

        # Count symbols by type
        symbol_counts: Dict[str, int] = {}
        for symbol in symbols:
            symbol_counts[symbol.symbol_type] = (
                symbol_counts.get(symbol.symbol_type, 0) + 1
            )

        lines = []
        lines.append("**Symbol Summary:**")
        for symbol_type in sorted(symbol_counts.keys()):
            count = symbol_counts[symbol_type]
            lines.append(f"- {symbol_type.title()}s: {count}")

        lines.append("")
        lines.append("**Notable Symbols:**")

        # Show some key symbols
        functions = [s for s in symbols if s.symbol_type == "function"]
        classes = [s for s in symbols if s.symbol_type == "class"]
        imports = [s for s in symbols if s.symbol_type == "import"]

        if classes:
            lines.append("*Classes:*")
            for cls in classes[:5]:  # Show first 5
                lines.append(f"  - {cls.name} (line {cls.line_number})")
            if len(classes) > 5:
                lines.append(f"  - ... and {len(classes) - 5} more")

        if functions:
            lines.append("*Functions:*")
            for func in functions[:5]:  # Show first 5
                params = f"({', '.join(func.parameters)})" if func.parameters else "()"
                lines.append(f"  - {func.name}{params} (line {func.line_number})")
            if len(functions) > 5:
                lines.append(f"  - ... and {len(functions) - 5} more")

        if imports:
            lines.append("*Key Imports:*")
            unique_imports = list(set(imp.name for imp in imports))
            for imp in sorted(unique_imports)[:10]:  # Show first 10
                lines.append(f"  - {imp}")
            if len(unique_imports) > 10:
                lines.append(f"  - ... and {len(unique_imports) - 10} more")

        return "\n".join(lines)

    def _generate_dependency_section(self, dependency_graph: DependencyGraph) -> str:
        """Generate the dependency graph section."""
        mermaid_graph = dependency_graph.generate_mermaid()

        if not mermaid_graph:
            return ""

        lines = ["## Dependency Graph", "", "```mermaid", mermaid_graph, "```", ""]

        return "\n".join(lines)
