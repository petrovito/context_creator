"""Module for creating context from files."""

import os
from pathlib import Path
from typing import Iterator, List, Optional

import pyperclip

from context_creator.file_iterator import FileIterator
from context_creator.types import FileInfo, FilterFunction, PathLike


class ContextCreator:
    """Class for creating context from files in a directory."""

    def __init__(
        self,
        root_dir: PathLike,
        file_filter: Optional[FilterFunction] = None,
        additional_exclude_patterns: List[str] = None,
    ):
        """
        Initialize the ContextCreator.

        Args:
            root_dir: The root directory to scan.
            file_filter: A function that returns True if a file should be included.
            additional_exclude_patterns: Additional patterns to exclude.
        """
        self.root_path = Path(root_dir).resolve()
        self.file_iterator = FileIterator(
            self.root_path,
            file_filter=file_filter,
            additional_exclude_patterns=additional_exclude_patterns,
        )

    def format_file_info(self, file_info: FileInfo) -> str:
        """
        Format a FileInfo object as a string.

        Args:
            file_info: The FileInfo object to format.

        Returns:
            A formatted string.
        """
        # Format: path/to/file:
        # ```filetype
        # content of file
        # ```
        return f"{file_info.relative_path}:\n```{file_info.file_type}\n{file_info.content}\n```"

    def create_context(self, copy_to_clipboard: bool = True) -> str:
        """
        Create context from files in the root directory.

        Args:
            copy_to_clipboard: Whether to copy the context to the clipboard.

        Returns:
            The generated context as a string.
        """
        # Iterate over files
        file_infos = list(self.file_iterator.iterate_files())
        
        # Sort files by path for consistent output
        file_infos.sort(key=lambda fi: str(fi.relative_path))
        
        # Format each file
        formatted_files = [self.format_file_info(file_info) for file_info in file_infos]
        
        # Join with double newlines
        context = "\n\n".join(formatted_files)
        
        # Copy to clipboard if requested
        if copy_to_clipboard:
            pyperclip.copy(context)
            print(f"Context copied to clipboard ({len(context)} characters, {len(file_infos)} files)")
        
        return context 