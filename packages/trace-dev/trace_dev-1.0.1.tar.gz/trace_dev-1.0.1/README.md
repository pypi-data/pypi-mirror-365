# trace-dev

A lightweight Python CLI that generates language-aware, recursive trace prompts for AI-driven development workflows. It scans project files, builds context, and outputs standardized prompts for downstream LLMs (e.g., via LiteLLM or multi-agent chains).

## Features

- **Recursive File Scanning**: Automatically discovers source files in configurable directories
- **Language Detection**: Supports Python, JavaScript, TypeScript, Go, Rust, and many more languages
- **AST Parsing**: Uses Tree-sitter for accurate symbol extraction (functions, classes, imports)
- **Context Generation**: Creates comprehensive project context with file structure and symbol overview
- **Dependency Graphs**: Generates mermaid diagrams showing module relationships
- **Customizable Templates**: Support for custom prompt templates via configuration
- **CLI Interface**: Easy-to-use command-line interface with multiple output options
- **Performance Optimized**: Scans up to 1000 files in under 2 seconds

## Installation

### From PyPI (when published)

```bash
pip install trace-dev
```

### From Source

```bash
git clone https://github.com/trace-dev/trace-dev.git
cd trace-dev
pip install -e .
```

## Usage

trace-dev is a command-line tool that generates AI-ready prompts from your codebase. Here are the main ways to use it:

```bash
# Generate a trace prompt for a specific task
trace-dev generate "Implement user authentication"

# Save the output to a file
trace-dev generate "Add API endpoints" --output trace.md

# Analyze your project structure
trace-dev info

# Create a configuration file
trace-dev init-config
```

For detailed command options and examples, see the Commands section below.

## Quick Start

📚 **New to trace-dev?** Start with the [Getting Started Tutorial](docs/tutorials/getting-started.md)

### Basic Usage

Generate a trace prompt for your current project:

```bash
trace-dev generate "Implement user authentication"
```

### Save to File

```bash
trace-dev generate "Add logging functionality" --output trace.md
```

### Analyze Project

```bash
trace-dev info
```

### Generate Configuration

```bash
trace-dev init-config
```

## Commands

### `generate`

Generate a trace prompt for a given task description.

```bash
trace-dev generate "TASK_DESCRIPTION" [OPTIONS]
```

**Options:**
- `-o, --output PATH`: Output file path (default: stdout)
- `-c, --config PATH`: Configuration file path
- `-r, --root PATH`: Root directory to scan (default: current directory)
- `--no-graph`: Disable dependency graph generation
- `-t, --template PATH`: Custom template file path
- `--scan-dirs DIRS`: Comma-separated list of directories to scan
- `-v, --verbose`: Enable verbose output

**Examples:**

```bash
# Basic usage
trace-dev generate "Implement caching layer"

# With custom configuration
trace-dev generate "Add error handling" --config my-config.yaml

# Scan specific directories only
trace-dev generate "Refactor utilities" --scan-dirs "src,lib"

# Save to file with verbose output
trace-dev generate "Add unit tests" --output trace.md --verbose
```

### `info`

Show project information and statistics.

```bash
trace-dev info [OPTIONS]
```

**Options:**
- `-r, --root PATH`: Root directory to analyze (default: current directory)
- `-c, --config PATH`: Configuration file path

**Example Output:**

```
Project Analysis: /path/to/project
==================================================
Total Files: 25
Languages: python, javascript
Has README: Yes
Config Files: 3
Total Symbols: 156

Symbol Breakdown:
  Classes: 12
  Functions: 89
  Imports: 34
  Variables: 21

Files by Language:
  Python: 15 files
  Javascript: 10 files
```

### `init-config`

Generate an example configuration file.

```bash
trace-dev init-config [OPTIONS]
```

**Options:**
- `-o, --output PATH`: Output path for config file (default: trace-dev.yaml)

## Configuration

Create a `trace-dev.yaml` file in your project root to customize behavior:

```yaml
# Directories to scan for source files
scan_dirs:
  - src
  - lib
  - app

# Patterns to ignore (gitignore-style)
ignore_patterns:
  - __pycache__/
  - "*.pyc"
  - node_modules/
  - .git/
  - dist/
  - build/

# File extension to language mapping
language_map:
  .py: python
  .js: javascript
  .jsx: javascript
  .ts: typescript
  .tsx: typescript
  .go: go
  .rs: rust

# Maximum file size to process (bytes)
max_file_size: 1048576  # 1MB

# Include dependency graph in output
include_graph: true

# Custom template file (optional)
template: custom_template.md
```

## Custom Templates

You can create custom prompt templates using Python string formatting. The template receives the following variables:

- `task_description`: The task description provided by the user
- `root_path`: Root directory path
- `total_files`: Number of files found
- `languages`: Comma-separated list of detected languages
- `has_readme`: "Yes" or "No"
- `config_files`: Comma-separated list of configuration files
- `file_structure`: Formatted file structure
- `language_breakdown`: Detailed breakdown by language
- `symbol_overview`: Summary of symbols found
- `dependency_graph`: Mermaid dependency graph (if enabled)
- `timestamp`: Generation timestamp
- `version`: Tool version

**Example Custom Template:**

```markdown
# Development Task: {task_description}

## Project: {root_path}
- Files: {total_files}
- Languages: {languages}

{file_structure}

{symbol_overview}

## Instructions
Please implement the requested changes following these guidelines:
1. Maintain existing code style and patterns
2. Add appropriate tests
3. Update documentation as needed

{dependency_graph}
```

## Supported Languages

trace-dev supports the following programming languages through Tree-sitter:

- **Python** (.py) - Full AST parsing
- **JavaScript** (.js, .jsx) - Full AST parsing  
- **TypeScript** (.ts, .tsx) - Full AST parsing
- **Go** (.go) - Language detection
- **Rust** (.rs) - Language detection
- **Java** (.java) - Language detection
- **C/C++** (.c, .cpp, .h, .hpp) - Language detection
- **C#** (.cs) - Language detection
- **PHP** (.php) - Language detection
- **Ruby** (.rb) - Language detection
- **Swift** (.swift) - Language detection
- **Kotlin** (.kt) - Language detection
- **Scala** (.scala) - Language detection

*Note: Languages marked as "Language detection" are recognized and counted but don't have full AST parsing yet.*

## Integration Examples

### With LangChain

```python
import subprocess
from langchain.prompts import PromptTemplate

# Generate trace prompt
result = subprocess.run([
    'trace-dev', 'generate', 'Add authentication',
    '--output', 'trace.md'
], capture_output=True, text=True)

# Use with LangChain
with open('trace.md', 'r') as f:
    trace_prompt = f.read()

# Continue with your LangChain workflow...
```

### With CI/CD

```yaml
# .github/workflows/trace.yml
name: Generate Trace Prompts
on: [push]

jobs:
  trace:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install trace-dev
        run: pip install trace-dev
      - name: Generate trace prompt
        run: |
          trace-dev generate "Review and improve code quality" \
            --output artifacts/trace-prompt.md
      - name: Upload artifacts
        uses: actions/upload-artifact@v2
        with:
          name: trace-prompt
          path: artifacts/
```

## Performance

trace-dev is designed for performance:

- Scans up to 1000 files in under 2 seconds
- Memory efficient with configurable file size limits
- Parallel processing for large codebases
- Smart caching of parsed results

## Development

### Setting up Development Environment

```bash
git clone https://github.com/trace-dev/trace-dev.git
cd trace-dev
pip install -e .
pip install -r requirements-dev.txt
```

### Running Tests

```bash
# Run all tests
python -m unittest discover tests -v

# Run specific test module
python -m unittest tests.test_parser -v

# Run with coverage
coverage run -m unittest discover tests
coverage report
```

### Project Structure

```
trace-dev/
├── src/trace_dev/           # Main package
│   ├── __init__.py         # Package initialization
│   ├── cli.py              # CLI interface
│   ├── scanner.py          # File scanning logic
│   ├── parser.py           # AST parsing and symbol extraction
│   └── prompt_generator.py # Prompt generation and templating
├── tests/                  # Test suite
│   ├── test_scanner.py     # Scanner tests
│   ├── test_parser.py      # Parser tests
│   ├── test_prompt_generator.py # Prompt generator tests
│   └── test_integration.py # Integration tests
├── docs/                   # Documentation
├── examples/               # Example configurations and templates
├── setup.py               # Package setup
├── requirements.txt       # Dependencies
└── README.md              # This file
```

## Contributing

We welcome contributions! Please see our comprehensive developer guides:

- **[Setup and Contribution Guide](docs/developer/setup-and-contribution.md)** - Development environment and workflow
- **[Testing and Quality Standards](docs/developer/testing-and-quality.md)** - Code quality and testing practices

### Areas for Contribution

- Additional language parsers (Go, Rust, Java, etc.)
- Enhanced dependency analysis
- Custom template gallery
- IDE integrations
- Performance optimizations

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Changelog

### v0.1.0 (Initial Release)

- Recursive file scanning with configurable directories
- Language detection for 20+ programming languages
- Tree-sitter AST parsing for Python, JavaScript, TypeScript
- Symbol extraction (functions, classes, imports, variables)
- Standardized trace prompt generation
- Mermaid dependency graph generation
- CLI interface with subcommands
- YAML configuration support
- Custom template system
- Comprehensive test suite (24 tests)
- Performance optimized (< 2s for 1000 files)

## Documentation

For comprehensive documentation including tutorials, how-to guides, API reference, and architecture details:

**📚 [Complete Documentation](docs/README.md)**

The documentation follows the Diátaxis framework with:
- **[Getting Started Tutorial](docs/tutorials/getting-started.md)** - Learn trace-dev with your first project
- **[How-To Guides](docs/how-to-guides/)** - Solve specific problems and integrate with AI tools  
- **[API Reference](docs/reference/)** - Complete CLI and Python API documentation
- **[Developer Guides](docs/developer/)** - Contribute to the project
- **[Architecture & Design](docs/explanations/)** - Understand how trace-dev works

## Support

- **Issues**: [GitHub Issues](https://github.com/trace-dev/trace-dev/issues)
- **Discussions**: [GitHub Discussions](https://github.com/trace-dev/trace-dev/discussions)
- **Documentation**: [Complete Documentation](docs/README.md)

## Related Projects

- [Tree-sitter](https://tree-sitter.github.io/) - Parser generator and incremental parsing library
- [LiteLLM](https://github.com/BerriAI/litellm) - Unified interface for LLM APIs
- [LangChain](https://github.com/hwchase17/langchain) - Framework for developing LLM applications

