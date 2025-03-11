"""Module for iterating over files in a file tree."""

import mimetypes
from pathlib import Path
from typing import Dict, Iterator, List, Optional

from context_creator.file_filter import FileFilter
from context_creator.file_tree_creator import FileTreeCreator
from context_creator.types import FileInfo, FileTree, FilterFunction, PathLike


class FileIterator:
    """Class for iterating over files in a file tree."""

    # Map of file extensions to language names
    EXTENSION_MAP = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".jsx": "jsx",
        ".tsx": "tsx",
        ".html": "html",
        ".css": "css",
        ".scss": "scss",
        ".json": "json",
        ".md": "markdown",
        ".yml": "yaml",
        ".yaml": "yaml",
        ".toml": "toml",
        ".ini": "ini",
        ".cfg": "ini",
        ".txt": "text",
        ".sh": "bash",
        ".bash": "bash",
        ".zsh": "bash",
        ".fish": "fish",
        ".c": "c",
        ".cpp": "cpp",
        ".h": "c",
        ".hpp": "cpp",
        ".java": "java",
        ".go": "go",
        ".rs": "rust",
        ".rb": "ruby",
        ".php": "php",
        ".swift": "swift",
        ".kt": "kotlin",
        ".kts": "kotlin",
        ".scala": "scala",
        ".sql": "sql",
        ".r": "r",
        ".dart": "dart",
        ".lua": "lua",
        ".ex": "elixir",
        ".exs": "elixir",
        ".erl": "erlang",
        ".hrl": "erlang",
        ".clj": "clojure",
        ".cs": "csharp",
        ".fs": "fsharp",
        ".pl": "perl",
        ".pm": "perl",
        ".hs": "haskell",
        ".lhs": "haskell",
    }

    def __init__(
        self,
        root_dir: PathLike,
        file_filter: Optional[FilterFunction] = None,
        additional_exclude_patterns: List[str] = None,
    ):
        """
        Initialize the FileIterator.

        Args:
            root_dir: The root directory to scan.
            file_filter: A function that returns True if a file should be included.
            additional_exclude_patterns: Additional patterns to exclude.
        """
        self.root_path = Path(root_dir).resolve()
        
        # Create a file filter if not provided
        if file_filter is None:
            filter_manager = FileFilter(
                self.root_path, 
                use_gitignore=True,
                additional_exclude_patterns=additional_exclude_patterns,
            )
            self.file_filter = filter_manager.create_filter()
        else:
            self.file_filter = file_filter
        
        # Create a file tree creator
        self.tree_creator = FileTreeCreator(self.root_path)

    def get_file_type(self, path: Path) -> str:
        """
        Get the file type (language) based on the file extension.

        Args:
            path: The path to the file.

        Returns:
            The file type as a string.
        """
        extension = path.suffix.lower()
        return self.EXTENSION_MAP.get(extension, "text")

    def read_file_content(self, path: Path) -> str:
        """
        Read the content of a file.

        Args:
            path: The path to the file.

        Returns:
            The content of the file as a string.
        """
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except UnicodeDecodeError:
            # If UTF-8 fails, try with Latin-1 (which can read any byte sequence)
            with open(path, "r", encoding="latin-1") as f:
                return f.read()

    def iterate_files(self) -> Iterator[FileInfo]:
        """
        Iterate over files in the root directory.

        Yields:
            FileInfo objects for each file.
        """
        # Create a file tree
        file_tree = self.tree_creator.create_file_tree()
        
        # Iterate over all files in the tree
        for dir_path, files in file_tree.items():
            for file_path in files:
                # Skip files that don't pass the filter
                if not self.file_filter(file_path):
                    continue
                    
                # Get the relative path from the root directory
                relative_path = file_path.relative_to(self.root_path)
                
                # Read the file content
                content = self.read_file_content(file_path)
                
                # Get the file type
                file_type = self.get_file_type(file_path)
                
                # Yield a FileInfo object
                yield FileInfo(
                    path=file_path,
                    relative_path=relative_path,
                    content=content,
                    file_type=file_type,
                ) 