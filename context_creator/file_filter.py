"""Module for filtering files based on various criteria."""

import mimetypes
import os
from pathlib import Path
from typing import List, Set

from context_creator.gitignore_manager import GitignoreManager
from context_creator.types import FilterFunction, PathLike


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
    
    # Default directories to exclude
    DEFAULT_EXCLUDE_DIRS = {".git"}

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
        
        # Add additional exclude patterns if provided
        if additional_exclude_patterns:
            self.exclude_patterns.update(additional_exclude_patterns)
        
        # Get the gitignore filter if requested
        self.gitignore_manager = None
        if self.use_gitignore:
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
            return False

        mime_type, _ = mimetypes.guess_type(str(path))
        if mime_type is None:
            # Try to read the file as text
            try:
                with open(path, "r", encoding="utf-8") as f:
                    f.read(1024)  # Read a small chunk to check if it's text
                return True
            except UnicodeDecodeError:
                return False
        
        return mime_type.startswith("text/")

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
        
        # Check if the path is inside a .git directory
        parts = abs_path.parts
        for exclude_dir in self.DEFAULT_EXCLUDE_DIRS:
            if exclude_dir in parts:
                return True
                
        return False

    def create_filter(self) -> FilterFunction:
        """
        Create a filter function for files.

        Returns:
            A function that returns True if a file should be included.
        """
        # Get the gitignore filter if available
        gitignore_filter = (
            self.gitignore_manager.get_gitignore_filter() 
            if self.gitignore_manager else lambda _: True
        )
        
        def file_filter(path: Path) -> bool:
            """Filter function for files."""
            # Skip directories
            if not path.is_file():
                return False
                
            # Skip files with binary extensions
            if path.suffix.lower() in self.BINARY_EXTENSIONS:
                return False
                
            # Skip files in excluded directories (like .git)
            if self.is_in_excluded_dir(path):
                return False
                
            # Skip files matching exclude patterns
            for pattern in self.exclude_patterns:
                if path.match(pattern):
                    return False
                    
            # Apply gitignore filter
            if not gitignore_filter(path):
                return False
                
            # Check if it's a text file
            return self.is_text_file(path)
        
        return file_filter 