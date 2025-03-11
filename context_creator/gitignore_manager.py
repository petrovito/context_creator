"""Module for managing .gitignore files and filtering files based on gitignore rules."""

import logging
import os
from pathlib import Path
from typing import Callable, Optional

import gitignore_parser

from context_creator.types import FilterFunction, PathLike

# Get logger
logger = logging.getLogger("context_creator")


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
        
        logger.debug(f"Initializing GitignoreManager for directory: {self.root_path}")
        
        if self.gitignore_path.exists():
            logger.debug(f"Found .gitignore file: {self.gitignore_path}")
            # Parse the .gitignore file
            self.matches = gitignore_parser.parse_gitignore(self.gitignore_path)
            
            # Log the contents of the .gitignore file
            try:
                with open(self.gitignore_path, "r") as f:
                    content = f.read().strip()
                    lines = content.split("\n")
                    non_empty_lines = [line for line in lines if line.strip() and not line.strip().startswith("#")]
                    logger.debug(f".gitignore contains {len(non_empty_lines)} non-empty, non-comment lines")
                    for line in non_empty_lines:
                        logger.debug(f"  .gitignore pattern: {line}")
            except Exception as e:
                logger.warning(f"Error reading .gitignore file: {e}")
        else:
            logger.debug("No .gitignore file found")

    def get_gitignore_filter(self) -> FilterFunction:
        """
        Create a filter function based on .gitignore rules.

        Returns:
            A function that returns True if a file should be included (not ignored).
        """
        logger.debug("Creating gitignore filter function")
        
        if self.matches is None:
            # If no .gitignore file exists, include all files
            logger.debug("No gitignore rules, including all files")
            return lambda path: True

        # Create a filter function that returns True if a file should be included
        def gitignore_filter(path: Path) -> bool:
            """Filter function for gitignore rules."""
            # Convert to absolute path if it's not already
            abs_path = path if path.is_absolute() else (self.root_path / path).resolve()
            
            # Check if the file is ignored by gitignore
            is_ignored = self.matches(str(abs_path))
            
            if is_ignored:
                rel_path = path.relative_to(self.root_path) if path.is_absolute() else path
                logger.debug(f"File is ignored by gitignore: {rel_path}")
                
            # Return True if the file should be included (not matched by gitignore)
            return not is_ignored

        return gitignore_filter 