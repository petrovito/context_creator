"""Module for creating a file tree from a directory."""

import os
from pathlib import Path
from typing import Dict, List

from context_creator.types import FileTree, PathLike


class FileTreeCreator:
    """Class for creating a file tree from a directory."""

    def __init__(self, root_dir: PathLike):
        """
        Initialize the FileTreeCreator.

        Args:
            root_dir: The root directory to scan.
        """
        self.root_path = Path(root_dir).resolve()
        if not self.root_path.exists():
            raise FileNotFoundError(f"Directory not found: {self.root_path}")
        if not self.root_path.is_dir():
            raise NotADirectoryError(f"Not a directory: {self.root_path}")

    def create_file_tree(self) -> FileTree:
        """
        Create a file tree from the root directory.

        Returns:
            A dictionary mapping directories to lists of files.
        """
        file_tree: FileTree = {}

        for dirpath, dirnames, filenames in os.walk(self.root_path):
            dir_path = Path(dirpath)
            file_tree[dir_path] = [dir_path / filename for filename in filenames]

        return file_tree 