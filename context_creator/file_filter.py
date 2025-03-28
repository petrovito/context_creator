"""Module for filtering files based on various criteria."""

import logging
import mimetypes
import os
from pathlib import Path
from typing import List, Set

from context_creator.gitignore_manager import GitignoreManager
from context_creator.types import FilterFunction, PathLike

# Get logger
logger = logging.getLogger("context_creator")


class FileFilter:
    """Class for filtering files based on various criteria."""

    # Common binary file extensions to exclude
    BINARY_EXTENSIONS = {
        ".pyc", ".pyo", ".so", ".o", ".a", ".lib", ".dll", ".exe", ".bin",
        ".dat", ".db", ".sqlite", ".sqlite3", ".db-shm", ".db-wal",
        ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".ico", ".tiff",
        ".mp3", ".mp4", ".avi", ".mov", ".flv", ".wav", ".ogg",
        ".zip", ".tar", ".gz", ".bz2", ".7z", ".rar",
        ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    }
    
    # Default directories to exclude (only those not typically in .gitignore)
    DEFAULT_EXCLUDE_DIRS = {".git", ".vscode"}
    
    # Default files to exclude - files that are typically not useful for LLM context
    # and might not be in standard .gitignore files
    DEFAULT_EXCLUDE_FILES = {
        # Version control
        ".gitignore",  # Explicitly exclude .gitignore since we're using it for filtering
        
        # Lock files that might not be gitignored in some projects
        "Cargo.lock",  # Rust - sometimes committed, sometimes not
        "package-lock.json",  # npm - sometimes committed
        "yarn.lock",  # Yarn - sometimes committed
        "pnpm-lock.yaml",  # pnpm - sometimes committed
        "composer.lock",  # PHP - sometimes committed
        "Gemfile.lock",  # Ruby - sometimes committed
        
        # Generated files that might not be in .gitignore
        "*.min.js",  # Minified JavaScript - sometimes committed
        "*.min.css",  # Minified CSS - sometimes committed
        "*.map",  # Source maps - sometimes committed
        
        # Large generated files that might be committed
        "yarn-error.log",  # Yarn error logs
        "npm-debug.log",  # npm debug logs
        
        # Configuration files that aren't useful for context
        ".editorconfig",  # Editor configuration
        ".prettierrc",  # Prettier configuration
        ".eslintrc",  # ESLint configuration
        ".stylelintrc",  # Stylelint configuration
        "tsconfig.json",  # TypeScript configuration
        "jsconfig.json",  # JavaScript configuration
        ".babelrc",  # Babel configuration
    }
    
    # Extensions that should always be considered text files
    # regardless of their MIME type
    ALWAYS_TEXT_EXTENSIONS = {
        ".rs",    # Rust
        ".go",    # Go
        ".ts",    # TypeScript
        ".tsx",   # TypeScript JSX
        ".jsx",   # JSX
        ".vue",   # Vue
        ".svelte", # Svelte
        ".kt",    # Kotlin
        ".kts",   # Kotlin Script
        ".swift", # Swift
        ".scala", # Scala
        ".elm",   # Elm
        ".hs",    # Haskell
        ".rb",    # Ruby
        ".php",   # PHP
        ".pl",    # Perl
        ".ex",    # Elixir
        ".exs",   # Elixir Script
        ".erl",   # Erlang
        ".hrl",   # Erlang Header
        ".clj",   # Clojure
        ".fs",    # F#
        ".fsx",   # F# Script
    }

    def __init__(
        self, 
        root_dir: PathLike, 
        use_gitignore: bool = True,
        additional_exclude_patterns: List[str] = None,
    ):
        """
        Initialize the FileFilter.

        Args:
            root_dir: The root directory.
            use_gitignore: Whether to use .gitignore rules.
            additional_exclude_patterns: Additional patterns to exclude.
        """
        self.root_path = Path(root_dir).resolve()
        self.use_gitignore = use_gitignore
        self.exclude_patterns: Set[str] = set()
        
        logger.debug(f"Initializing FileFilter for directory: {self.root_path}")
        logger.debug(f"Using gitignore: {self.use_gitignore}")
        
        # Add additional exclude patterns if provided
        if additional_exclude_patterns:
            self.exclude_patterns.update(additional_exclude_patterns)
            logger.debug(f"Additional exclude patterns: {self.exclude_patterns}")
        
        # Get the gitignore filter if requested
        self.gitignore_manager = None
        if self.use_gitignore:
            logger.debug("Creating GitignoreManager")
            self.gitignore_manager = GitignoreManager(self.root_path)

    def is_text_file(self, path: Path) -> bool:
        """
        Check if a file is a text file based on its MIME type.

        Args:
            path: The path to the file.

        Returns:
            True if the file is a text file, False otherwise.
        """
        if not path.is_file():
            logger.debug(f"Not a file: {path}")
            return False
            
        # Check if the file extension is in our list of always-text extensions
        if path.suffix.lower() in self.ALWAYS_TEXT_EXTENSIONS:
            logger.debug(f"File is text (by extension override): {path}")
            return True

        mime_type, _ = mimetypes.guess_type(str(path))
        if mime_type is None:
            # Try to read the file as text
            try:
                with open(path, "r", encoding="utf-8") as f:
                    f.read(1024)  # Read a small chunk to check if it's text
                logger.debug(f"File is text (read test): {path}")
                return True
            except UnicodeDecodeError:
                logger.debug(f"File is not text (UnicodeDecodeError): {path}")
                return False
        
        is_text = mime_type.startswith("text/")
        logger.debug(f"File is {'text' if is_text else 'not text'} (mime type: {mime_type}): {path}")
        return is_text

    def is_in_excluded_dir(self, path: Path) -> bool:
        """
        Check if a path is inside an excluded directory.

        Args:
            path: The path to check.

        Returns:
            True if the path is inside an excluded directory, False otherwise.
        """
        # Convert to absolute path if it's not already
        abs_path = path if path.is_absolute() else (self.root_path / path).resolve()
        
        # Check if the path is inside an excluded directory
        parts = abs_path.parts
        for exclude_dir in self.DEFAULT_EXCLUDE_DIRS:
            if exclude_dir in parts:
                logger.debug(f"File is in excluded directory '{exclude_dir}': {path}")
                return True
                
        return False
        
    def is_excluded_file(self, path: Path) -> bool:
        """
        Check if a file is in the list of excluded files.
        
        Args:
            path: The path to check.
            
        Returns:
            True if the file is excluded, False otherwise.
        """
        # Check exact filename matches
        if path.name in self.DEFAULT_EXCLUDE_FILES:
            logger.debug(f"File is in excluded files list: {path}")
            return True
            
        # Check pattern matches (for entries with wildcards)
        for pattern in self.DEFAULT_EXCLUDE_FILES:
            if "*" in pattern and path.match(pattern):
                logger.debug(f"File matches excluded pattern '{pattern}': {path}")
                return True
                
        return False

    def create_filter(self) -> FilterFunction:
        """
        Create a filter function for files.

        Returns:
            A function that returns True if a file should be included.
        """
        logger.debug("Creating file filter function")
        
        # Get the gitignore filter if available
        gitignore_filter = (
            self.gitignore_manager.get_gitignore_filter() 
            if self.gitignore_manager else lambda _: True
        )
        
        def file_filter(path: Path) -> bool:
            """Filter function for files."""
            # Skip directories
            if not path.is_file():
                logger.debug(f"Skipping directory: {path}")
                return False
                
            # Skip files with binary extensions
            if path.suffix.lower() in self.BINARY_EXTENSIONS:
                logger.debug(f"Skipping binary file (by extension): {path}")
                return False
                
            # Skip files in excluded directories (like .git)
            if self.is_in_excluded_dir(path):
                return False
                
            # Skip excluded files (like .gitignore)
            if self.is_excluded_file(path):
                return False
                
            # Skip files matching exclude patterns
            for pattern in self.exclude_patterns:
                if path.match(pattern):
                    logger.debug(f"File matches exclude pattern '{pattern}': {path}")
                    return False
                    
            # Apply gitignore filter
            if not gitignore_filter(path):
                logger.debug(f"File is excluded by gitignore: {path}")
                return False
                
            # Check if it's a text file
            is_text = self.is_text_file(path)
            if not is_text:
                logger.debug(f"File is not a text file: {path}")
            return is_text
        
        return file_filter 