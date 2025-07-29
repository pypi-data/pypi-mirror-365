# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Development and Testing

```bash
# Install development dependencies
pip install -e .

# Run all tests
python -m unittest discover tests -v

# Run specific test module
python -m unittest tests.test_scanner -v
python -m unittest tests.test_parser -v
python -m unittest tests.test_prompt_generator -v
python -m unittest tests.test_integration -v

# Run tests with coverage (install coverage first: pip install coverage)
coverage run -m unittest discover tests
coverage report
coverage html  # Generate HTML coverage report

# Install the CLI tool in development mode
pip install -e .

# Test the CLI commands
trace-dev --help
trace-dev generate "Test task" --verbose
trace-dev info
trace-dev init-config
```

### Building and Distribution

```bash
# Build distribution packages
python setup.py sdist bdist_wheel

# Check package before uploading
pip install twine
twine check dist/*

# Upload to PyPI (requires credentials)
twine upload dist/*
```

### Code Quality

```bash
# Format code with black (install first: pip install black)
black src/ tests/

# Lint with flake8 (install first: pip install flake8)
flake8 src/ tests/ --max-line-length=120

# Type checking with mypy (install first: pip install mypy)
mypy src/ tests/ --ignore-missing-imports
```

## Architecture Overview

### Core Components

1. **src/trace_dev/scanner.py**: FileScanner class handles recursive directory traversal and file discovery
   - Uses pathspec for gitignore-style pattern matching
   - Configurable language detection via file extensions
   - Respects both default and custom ignore patterns

2. **src/trace_dev/parser.py**: CodeParser and language-specific parsers for AST analysis
   - Uses tree-sitter for accurate parsing
   - Currently supports Python, JavaScript, and TypeScript
   - Extracts symbols (functions, classes, imports, variables)
   - Extensible design for adding new language parsers

3. **src/trace_dev/prompt_generator.py**: PromptGenerator combines scanning and parsing to create prompts
   - PromptTemplate class for customizable output formats
   - DependencyGraph generates mermaid diagrams
   - Aggregates project context and symbol information

4. **src/trace_dev/cli.py**: Click-based command-line interface
   - Three main commands: generate, info, init-config
   - Configuration management via YAML files
   - Support for custom templates and scan directories

### Data Flow

1. User invokes CLI command → cli.py processes arguments
2. Config loads from YAML file or defaults → Config class
3. FileScanner scans directories → returns files grouped by language
4. CodeParser processes each file → extracts Symbol objects
5. PromptGenerator aggregates data → renders template with context
6. Output written to stdout or file

### Key Design Patterns

- **Strategy Pattern**: Language-specific parsers inherit from LanguageParser base class
- **Template Pattern**: PromptTemplate allows customizable output formats
- **Configuration Pattern**: Centralized Config class with defaults and overrides
- **Factory Pattern**: CodeParser manages language-specific parser instances

### Testing Structure

- **test_scanner.py**: Tests file discovery, language detection, ignore patterns
- **test_parser.py**: Tests AST parsing for each supported language
- **test_prompt_generator.py**: Tests prompt generation and template rendering
- **test_integration.py**: End-to-end tests of the complete workflow

### Entry Point

The package is configured as a module in setup.py:
- Package source is in the src/ directory
- Entry point: `trace-dev=trace_dev.cli:cli`
- This means the CLI imports from `trace_dev.*` namespace

### Dependencies

- **click**: CLI framework
- **tree-sitter**: AST parsing
- **tree-sitter-{language}**: Language-specific parsers
- **pyyaml**: Configuration file parsing
- **pathspec**: Gitignore-style pattern matching

### Configuration

The tool looks for configuration in this order:
1. Command-line specified config file (--config)
2. trace-dev.yaml in current directory
3. trace-dev.yml in current directory
4. .trace-dev.yaml in current directory
5. Built-in defaults

### Performance Considerations

- File size limit (default 1MB) prevents parsing very large files
- Ignore patterns reduce unnecessary file scanning
- Symbol extraction is memory-efficient (streaming)
- Designed to handle up to 1000 files in under 2 seconds