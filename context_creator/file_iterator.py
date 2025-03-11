"""Module for iterating over files in a file tree."""

import logging
import mimetypes
from pathlib import Path
from typing import Dict, Iterator, List, Optional

from context_creator.file_filter import FileFilter
from context_creator.file_tree_creator import FileTreeCreator
from context_creator.types import FileInfo, FileTree, FilterFunction, PathLike

# Get logger
logger = logging.getLogger("context_creator")


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
        logger.debug(f"Initializing FileIterator for directory: {self.root_path}")
        
        # Create a file filter if not provided
        if file_filter is None:
            logger.debug("Creating default file filter")
            filter_manager = FileFilter(
                self.root_path, 
                use_gitignore=True,
                additional_exclude_patterns=additional_exclude_patterns,
            )
            self.file_filter = filter_manager.create_filter()
        else:
            logger.debug("Using provided file filter")
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
        file_type = self.EXTENSION_MAP.get(extension, "text")
        logger.debug(f"File type for {path.name}: {file_type}")
        return file_type

    def read_file_content(self, path: Path) -> str:
        """
        Read the content of a file.

        Args:
            path: The path to the file.

        Returns:
            The content of the file as a string.
        """
        logger.debug(f"Reading file content: {path}")
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                logger.debug(f"Read {len(content)} characters from {path}")
                return content
        except UnicodeDecodeError:
            logger.debug(f"UTF-8 decode error for {path}, trying Latin-1")
            # If UTF-8 fails, try with Latin-1 (which can read any byte sequence)
            with open(path, "r", encoding="latin-1") as f:
                content = f.read()
                logger.debug(f"Read {len(content)} characters from {path} using Latin-1")
                return content
        except Exception as e:
            logger.warning(f"Error reading file {path}: {e}")
            return f"[Error reading file: {e}]"

    def iterate_files(self) -> Iterator[FileInfo]:
        """
        Iterate over files in the root directory.

        Yields:
            FileInfo objects for each file.
        """
        logger.debug(f"Iterating over files in {self.root_path}")
        
        # Create a file tree
        file_tree = self.tree_creator.create_file_tree()
        
        # Count total files for logging
        total_files = sum(len(files) for files in file_tree.values())
        included_files = 0
        excluded_files = 0
        
        logger.debug(f"Found {total_files} total files in the file tree")
        
        # Iterate over all files in the tree
        for dir_path, files in file_tree.items():
            logger.debug(f"Processing directory: {dir_path.relative_to(self.root_path) if dir_path != self.root_path else '.'} ({len(files)} files)")
            
            for file_path in files:
                # Skip files that don't pass the filter
                if not self.file_filter(file_path):
                    excluded_files += 1
                    logger.debug(f"Excluding file: {file_path.relative_to(self.root_path)}")
                    continue
                    
                included_files += 1
                
                # Get the relative path from the root directory
                relative_path = file_path.relative_to(self.root_path)
                logger.debug(f"Including file: {relative_path}")
                
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
        
        logger.debug(f"Iteration complete. Included {included_files} files, excluded {excluded_files} files") 