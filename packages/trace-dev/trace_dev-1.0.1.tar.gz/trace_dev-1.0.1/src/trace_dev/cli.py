"""
CLI interface for trace-dev.
Provides command-line interface for generating trace prompts.
"""

import click
import pathlib
import yaml
import sys
from typing import Optional, Dict
from .prompt_generator import PromptGenerator, PromptTemplate
from . import __version__


class Config:
    """Configuration management for trace-dev."""

    DEFAULT_CONFIG = {
        "scan_dirs": ["src", "lib", "app", "components", "modules", "packages"],
        "ignore_patterns": [
            "__pycache__/",
            "*.pyc",
            "node_modules/",
            ".git/",
            ".venv/",
            "venv/",
            "dist/",
            "build/",
        ],
        "language_map": {
            ".py": "python",
            ".js": "javascript",
            ".jsx": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".go": "go",
            ".rs": "rust",
        },
        "max_file_size": 1048576,  # 1MB
        "include_graph": True,
        "template": None,  # Use default template
    }

    def __init__(self, config_path: Optional[str] = None):
        self.config = self.DEFAULT_CONFIG.copy()

        if config_path:
            self.load_config(config_path)
        else:
            # Try to find config file in current directory
            for config_file in ["trace-dev.yaml", "trace-dev.yml", ".trace-dev.yaml"]:
                if pathlib.Path(config_file).exists():
                    self.load_config(config_file)
                    break

    def load_config(self, config_path: str):
        """Load configuration from YAML file."""
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                user_config = yaml.safe_load(f)

            if user_config:
                self.config.update(user_config)
                click.echo(f"Loaded configuration from {config_path}", err=True)
        except (FileNotFoundError, yaml.YAMLError) as e:
            click.echo(
                f"Warning: Could not load config file {config_path}: {e}", err=True
            )

    def get(self, key: str, default=None):
        """Get configuration value."""
        return self.config.get(key, default)

    def save_example_config(self, path: str):
        """Save an example configuration file."""
        example_config = {
            "scan_dirs": ["src", "lib"],
            "ignore_patterns": ["__pycache__/", "*.pyc", "node_modules/"],
            "language_map": {
                ".py": "python",
                ".js": "javascript",
                ".ts": "typescript",
            },
            "max_file_size": 1048576,
            "include_graph": True,
            "template": "custom_template.md",
        }

        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(example_config, f, default_flow_style=False, sort_keys=False)


def load_custom_template(template_path: str) -> Optional[PromptTemplate]:
    """Load a custom template from file."""
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            template_content = f.read()
        return PromptTemplate(template_content)
    except (FileNotFoundError, OSError) as e:
        click.echo(f"Warning: Could not load template {template_path}: {e}", err=True)
        return None


@click.group(invoke_without_command=True)
@click.pass_context
@click.version_option(version=__version__, prog_name="trace-dev")
def cli(ctx):
    """trace-dev: Generate language-aware trace prompts for AI development."""
    if ctx.invoked_subcommand is None:
        # If no subcommand is provided, show help
        click.echo(ctx.get_help())


@cli.command()
@click.argument("task_description", required=True)
@click.option(
    "--output", "-o", help="Output file path. If not specified, prints to stdout."
)
@click.option("--config", "-c", help="Path to configuration file (YAML).")
@click.option(
    "--root",
    "-r",
    default=".",
    help="Root directory to scan (default: current directory).",
)
@click.option("--no-graph", is_flag=True, help="Disable dependency graph generation.")
@click.option("--template", "-t", help="Path to custom template file.")
@click.option("--scan-dirs", help="Comma-separated list of directories to scan.")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output.")
def generate(
    task_description: str,
    output: Optional[str],
    config: Optional[str],
    root: str,
    no_graph: bool,
    template: Optional[str],
    scan_dirs: Optional[str],
    verbose: bool,
):
    """Generate a trace prompt for the given task description."""
    # Implementation moved from main function
    if verbose:
        click.echo(f"trace-dev v{__version__}", err=True)
        click.echo(f"Scanning root: {root}", err=True)

    # Load configuration
    cfg = Config(config)

    # Override config with command line options
    if no_graph:
        cfg.config["include_graph"] = False

    if scan_dirs:
        cfg.config["scan_dirs"] = [d.strip() for d in scan_dirs.split(",")]

    # Load custom template if specified
    custom_template = None
    template_path = template or cfg.get("template")
    if template_path:
        custom_template = load_custom_template(template_path)

    if verbose and template_path:
        if custom_template:
            click.echo(f"Using custom template: {template_path}", err=True)
        else:
            click.echo(f"Failed to load template: {template_path}", err=True)

    try:
        # Validate root path
        root_path = pathlib.Path(root).resolve()
        if not root_path.exists():
            click.echo(f"Error: Root path does not exist: {root}", err=True)
            sys.exit(1)
        if not root_path.is_dir():
            click.echo(f"Error: Root path is not a directory: {root}", err=True)
            sys.exit(1)

        # Create prompt generator
        generator = PromptGenerator(
            root_path=root,
            template=custom_template,
            include_graph=cfg.get("include_graph", True),
        )

        # Override scanner configuration
        generator.scanner.scan_dirs = cfg.get("scan_dirs")
        generator.scanner.language_map.update(cfg.get("language_map", {}))
        generator.scanner.max_file_size = cfg.get("max_file_size", 1048576)

        if verbose:
            click.echo(f"Scanning directories: {generator.scanner.scan_dirs}", err=True)
            click.echo(
                f"Supported languages: {list(generator.parser.get_supported_languages())}",
                err=True,
            )

        # Generate prompt
        prompt = generator.generate_prompt(task_description)

        # Output prompt
        if output:
            output_path = pathlib.Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(prompt)

            if verbose:
                click.echo(f"Prompt written to: {output_path}", err=True)
            else:
                click.echo(f"Prompt saved to {output_path}")
        else:
            click.echo(prompt)

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        if verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


@cli.command()
@click.option(
    "--output",
    "-o",
    default="trace-dev.yaml",
    help="Output path for the example config file.",
)
def init_config(output: str):
    """Generate an example configuration file."""
    config = Config()
    config.save_example_config(output)
    click.echo(f"Example configuration saved to {output}")
    click.echo("Edit this file to customize trace-dev behavior.")


@cli.command()
@click.option(
    "--root",
    "-r",
    default=".",
    help="Root directory to analyze (default: current directory).",
)
@click.option("--config", "-c", help="Path to configuration file (YAML).")
def info(root: str, config: Optional[str]):
    """Show project information and statistics."""
    from .scanner import FileScanner
    from .parser import CodeParser

    cfg = Config(config)
    scanner = FileScanner(root)
    parser = CodeParser()

    # Override scanner configuration
    scanner.scan_dirs = cfg.get("scan_dirs")
    scanner.language_map.update(cfg.get("language_map", {}))

    # Scan project
    files_by_language = scanner.scan()
    project_info = scanner.get_project_info()

    # Parse files for symbol counts
    total_symbols = 0
    symbols_by_type: Dict[str, int] = {}

    for language, files in files_by_language.items():
        if parser.is_language_supported(language):
            for file_path in files:
                symbols = parser.parse_file(file_path, language)
                total_symbols += len(symbols)
                for symbol in symbols:
                    symbols_by_type[symbol.symbol_type] = (
                        symbols_by_type.get(symbol.symbol_type, 0) + 1
                    )

    # Display information
    click.echo(f"Project Analysis: {project_info['root_path']}")
    click.echo("=" * 50)
    click.echo(f"Total Files: {project_info['total_files']}")
    click.echo(f"Languages: {', '.join(sorted(project_info['languages']))}")
    click.echo(f"Has README: {'Yes' if project_info['has_readme'] else 'No'}")
    click.echo(f"Config Files: {len(project_info['config_files'])}")
    click.echo(f"Total Symbols: {total_symbols}")

    if symbols_by_type:
        click.echo("\nSymbol Breakdown:")
        for symbol_type, count in sorted(symbols_by_type.items()):
            click.echo(f"  {symbol_type.title()}s: {count}")

    click.echo("\nFiles by Language:")
    for language in sorted(files_by_language.keys()):
        files = files_by_language[language]
        click.echo(f"  {language.title()}: {len(files)} files")


if __name__ == "__main__":
    cli()
