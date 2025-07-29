"""
File scanner module for trace-dev CLI.
Handles recursive directory scanning and file discovery.
"""

import pathlib
from typing import List, Dict, Optional, Any
from pathspec import PathSpec
from pathspec.patterns import GitWildMatchPattern


class FileScanner:
    """Recursively scans directories for source code files."""

    # Default file extensions to language mapping
    DEFAULT_LANGUAGE_MAP = {
        ".py": "python",
        ".js": "javascript",
        ".jsx": "javascript",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".go": "go",
        ".rs": "rust",
        ".java": "java",
        ".c": "c",
        ".cpp": "cpp",
        ".cc": "cpp",
        ".cxx": "cpp",
        ".h": "c",
        ".hpp": "cpp",
        ".cs": "csharp",
        ".php": "php",
        ".rb": "ruby",
        ".swift": "swift",
        ".kt": "kotlin",
        ".scala": "scala",
        ".clj": "clojure",
        ".hs": "haskell",
        ".ml": "ocaml",
        ".fs": "fsharp",
        ".elm": "elm",
        ".dart": "dart",
        ".lua": "lua",
        ".r": "r",
        ".R": "r",
        ".m": "matlab",
        ".pl": "perl",
        ".sh": "bash",
        ".bash": "bash",
        ".zsh": "zsh",
        ".fish": "fish",
        ".ps1": "powershell",
        ".sql": "sql",
        ".json": "json",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".toml": "toml",
        ".xml": "xml",
        ".html": "html",
        ".htm": "html",
        ".css": "css",
        ".scss": "scss",
        ".sass": "sass",
        ".less": "less",
        ".md": "markdown",
        ".markdown": "markdown",
        ".rst": "rst",
        ".tex": "latex",
        ".vim": "vim",
        ".dockerfile": "dockerfile",
        ".Dockerfile": "dockerfile",
    }

    # Default directories to scan
    DEFAULT_SCAN_DIRS = ["src", "lib", "app", "components", "modules", "packages"]

    # Default ignore patterns (similar to .gitignore)
    DEFAULT_IGNORE_PATTERNS = [
        "__pycache__/",
        "*.pyc",
        "*.pyo",
        "*.pyd",
        ".Python",
        "build/",
        "develop-eggs/",
        "dist/",
        "downloads/",
        "eggs/",
        ".eggs/",
        "lib/",
        "lib64/",
        "parts/",
        "sdist/",
        "var/",
        "wheels/",
        "*.egg-info/",
        ".installed.cfg",
        "*.egg",
        ".venv/",
        "venv/",
        ".env",
        "node_modules/",
        ".git/",
        ".svn/",
        ".hg/",
        ".bzr/",
        "target/",
        "bin/",
        "obj/",
        "*.class",
        "*.jar",
        "*.war",
        "*.ear",
        "*.zip",
        "*.tar.gz",
        "*.rar",
        ".DS_Store",
        "Thumbs.db",
        "*.log",
        "*.tmp",
        "*.temp",
        ".idea/",
        ".vscode/",
        "*.swp",
        "*.swo",
        "*~",
    ]

    def __init__(
        self,
        root_path: str = ".",
        scan_dirs: Optional[List[str]] = None,
        language_map: Optional[Dict[str, str]] = None,
        ignore_patterns: Optional[List[str]] = None,
        max_file_size: int = 1024 * 1024,
    ):  # 1MB default
        """
        Initialize the file scanner.

        Args:
            root_path: Root directory to scan from
            scan_dirs: List of subdirectories to scan (if None, scans all)
            language_map: Custom file extension to language mapping
            ignore_patterns: Custom ignore patterns
            max_file_size: Maximum file size to process in bytes
        """
        self.root_path = pathlib.Path(root_path).resolve()
        self.scan_dirs = scan_dirs or self.DEFAULT_SCAN_DIRS
        self.language_map = language_map or self.DEFAULT_LANGUAGE_MAP.copy()
        self.max_file_size = max_file_size

        # Set up ignore patterns
        ignore_patterns = ignore_patterns or self.DEFAULT_IGNORE_PATTERNS
        self.ignore_spec = PathSpec.from_lines(GitWildMatchPattern, ignore_patterns)

        # Load .gitignore if it exists
        gitignore_path = self.root_path / ".gitignore"
        if gitignore_path.exists():
            with open(gitignore_path, "r", encoding="utf-8") as f:
                gitignore_patterns = f.read().splitlines()
            # gitignore_spec = PathSpec.from_lines(
            #     GitWildMatchPattern, gitignore_patterns
            # )
            # Combine with default ignore patterns
            self.ignore_spec = PathSpec.from_lines(
                GitWildMatchPattern, ignore_patterns + gitignore_patterns
            )

    def should_ignore(self, file_path: pathlib.Path) -> bool:
        """Check if a file should be ignored based on ignore patterns."""
        try:
            # Resolve both paths to handle symlinks (e.g., /var -> /private/var on macOS)
            resolved_file_path = file_path.resolve()
            resolved_root_path = self.root_path.resolve()
            relative_path = resolved_file_path.relative_to(resolved_root_path)
            return self.ignore_spec.match_file(str(relative_path))
        except ValueError:
            # If relative_to fails, the file is not under root_path, so ignore it
            return True

    def detect_language(self, file_path: pathlib.Path) -> Optional[str]:
        """Detect the programming language of a file based on its extension."""
        suffix = file_path.suffix.lower()
        return self.language_map.get(suffix)

    def is_valid_source_file(self, file_path: pathlib.Path) -> bool:
        """Check if a file is a valid source code file to process."""
        # Check if file should be ignored
        if self.should_ignore(file_path):
            return False

        # Check if it's a regular file
        if not file_path.is_file():
            return False

        # Check file size
        try:
            if file_path.stat().st_size > self.max_file_size:
                return False
        except OSError:
            return False

        # Check if we can detect the language
        if self.detect_language(file_path) is None:
            return False

        return True

    def scan_directory(self, directory: pathlib.Path) -> List[pathlib.Path]:
        """Recursively scan a directory for source files."""
        source_files = []

        try:
            for item in directory.rglob("*"):
                if self.is_valid_source_file(item):
                    source_files.append(item)
        except (OSError, PermissionError) as e:
            print(f"Warning: Could not scan directory {directory}: {e}")

        return source_files

    def scan(self) -> Dict[str, List[pathlib.Path]]:
        """
        Scan for source files and group them by language.

        Returns:
            Dictionary mapping language names to lists of file paths
        """
        all_files = []

        # If scan_dirs is specified, only scan those directories
        if self.scan_dirs:
            for scan_dir in self.scan_dirs:
                dir_path = self.root_path / scan_dir
                if dir_path.exists() and dir_path.is_dir():
                    all_files.extend(self.scan_directory(dir_path))
        else:
            # Scan the entire root directory
            all_files.extend(self.scan_directory(self.root_path))

        # Group files by language
        files_by_language: Dict[str, List[pathlib.Path]] = {}
        for file_path in all_files:
            language = self.detect_language(file_path)
            if language:
                if language not in files_by_language:
                    files_by_language[language] = []
                files_by_language[language].append(file_path)

        return files_by_language

    def get_project_info(self) -> Dict[str, Any]:
        """Get basic project information."""
        info: Dict[str, Any] = {
            "root_path": str(self.root_path),
            "has_readme": False,
            "readme_files": [],
            "config_files": [],
            "total_files": 0,
            "languages": set(),
        }

        # Look for README files
        readme_patterns = ["README*", "readme*", "Readme*"]
        for pattern in readme_patterns:
            for readme_file in self.root_path.glob(pattern):
                if readme_file.is_file():
                    info["readme_files"].append(
                        str(readme_file.relative_to(self.root_path))
                    )
                    info["has_readme"] = True

        # Look for common config files
        config_patterns = [
            "package.json",
            "requirements.txt",
            "Pipfile",
            "pyproject.toml",
            "Cargo.toml",
            "go.mod",
            "pom.xml",
            "build.gradle",
            "Makefile",
            "CMakeLists.txt",
            "Dockerfile",
            "docker-compose.yml",
            ".gitignore",
            ".env*",
            "tsconfig.json",
            "webpack.config.js",
        ]
        for pattern in config_patterns:
            for config_file in self.root_path.glob(pattern):
                if config_file.is_file():
                    info["config_files"].append(
                        str(config_file.relative_to(self.root_path))
                    )

        # Get file statistics
        files_by_language = self.scan()
        info["total_files"] = sum(len(files) for files in files_by_language.values())
        info["languages"] = set(files_by_language.keys())

        return info
