"""Module for creating a file tree from a directory."""

import logging
import os
from pathlib import Path
from typing import Dict, List

from context_creator.types import FileTree, PathLike

# Get logger
logger = logging.getLogger("context_creator")


class FileTreeCreator:
    """Class for creating a file tree from a directory."""

    def __init__(self, root_dir: PathLike):
        """
        Initialize the FileTreeCreator.

        Args:
            root_dir: The root directory to scan.
        """
        self.root_path = Path(root_dir).resolve()
        
        logger.debug(f"Initializing FileTreeCreator for directory: {self.root_path}")
        
        if not self.root_path.exists():
            logger.error(f"Directory not found: {self.root_path}")
            raise FileNotFoundError(f"Directory not found: {self.root_path}")
        if not self.root_path.is_dir():
            logger.error(f"Not a directory: {self.root_path}")
            raise NotADirectoryError(f"Not a directory: {self.root_path}")

    def create_file_tree(self) -> FileTree:
        """
        Create a file tree from the root directory.

        Returns:
            A dictionary mapping directories to lists of files.
        """
        logger.debug(f"Creating file tree for directory: {self.root_path}")
        
        file_tree: FileTree = {}
        total_dirs = 0
        total_files = 0

        for dirpath, dirnames, filenames in os.walk(self.root_path):
            dir_path = Path(dirpath)
            total_dirs += 1
            
            # Add files to the file tree
            file_paths = [dir_path / filename for filename in filenames]
            file_tree[dir_path] = file_paths
            total_files += len(file_paths)
            
            rel_path = dir_path.relative_to(self.root_path) if dir_path != self.root_path else Path(".")
            logger.debug(f"Found directory: {rel_path} with {len(file_paths)} files")

        logger.debug(f"File tree created with {total_dirs} directories and {total_files} files")
        return file_tree 