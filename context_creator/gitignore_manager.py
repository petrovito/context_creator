"""Module for managing .gitignore files and filtering files based on gitignore rules."""

import os
from pathlib import Path
from typing import Callable, Optional

import gitignore_parser

from context_creator.types import FilterFunction, PathLike


class GitignoreManager:
    """Class for managing .gitignore files and filtering files based on gitignore rules."""

    def __init__(self, root_dir: PathLike):
        """
        Initialize the GitignoreManager.

        Args:
            root_dir: The root directory containing the .gitignore file.
        """
        self.root_path = Path(root_dir).resolve()
        self.gitignore_path = self.root_path / ".gitignore"
        self.matches = None
        
        if self.gitignore_path.exists():
            # Parse the .gitignore file
            self.matches = gitignore_parser.parse_gitignore(self.gitignore_path)

    def get_gitignore_filter(self) -> FilterFunction:
        """
        Create a filter function based on .gitignore rules.

        Returns:
            A function that returns True if a file should be included (not ignored).
        """
        if self.matches is None:
            # If no .gitignore file exists, include all files
            return lambda path: True

        # Create a filter function that returns True if a file should be included
        def gitignore_filter(path: Path) -> bool:
            # Convert to absolute path if it's not already
            abs_path = path if path.is_absolute() else (self.root_path / path).resolve()
            # Return True if the file should be included (not matched by gitignore)
            return not self.matches(str(abs_path))

        return gitignore_filter 