"""Tests for the ContextCreator class."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from context_creator.context_creator import ContextCreator
from context_creator.types import FileInfo


def test_format_file_info():
    """Test formatting a FileInfo object."""
    # Create a FileInfo object
    file_info = FileInfo(
        path=Path("/path/to/file.py"),
        relative_path=Path("file.py"),
        content="def hello():\n    print('Hello, world!')",
        file_type="python",
    )
    
    # Create a ContextCreator instance
    creator = ContextCreator(".")
    
    # Format the FileInfo object
    formatted = creator.format_file_info(file_info)
    
    # Check the formatted string
    expected = "file.py:\n```python\ndef hello():\n    print('Hello, world!')\n```"
    assert formatted == expected


@patch("pyperclip.copy")
def test_create_context(mock_copy):
    """Test creating context from files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create some files
        file_paths = {
            "file1.py": "def func1():\n    return 1",
            "file2.txt": "This is a text file",
            "subdir/file3.md": "# Markdown file",
        }
        
        for rel_path, content in file_paths.items():
            abs_path = os.path.join(temp_dir, rel_path)
            os.makedirs(os.path.dirname(abs_path), exist_ok=True)
            with open(abs_path, "w") as f:
                f.write(content)
        
        # Create a ContextCreator instance with a custom filter that includes all files
        creator = ContextCreator(
            temp_dir,
            file_filter=lambda path: True,
        )
        
        # Create context
        with patch("builtins.print") as mock_print:
            context = creator.create_context(copy_to_clipboard=True)
        
        # Check that the context contains all files
        assert "file1.py:" in context
        assert "```python" in context
        assert "def func1():" in context
        assert "file2.txt:" in context
        assert "```text" in context
        assert "This is a text file" in context
        assert "file3.md:" in context
        assert "```markdown" in context
        assert "# Markdown file" in context
        
        # Check that the context was copied to the clipboard
        mock_copy.assert_called_once_with(context)
        
        # Check that a message was printed
        mock_print.assert_called_once()


@patch("pyperclip.copy")
def test_create_context_no_clipboard(mock_copy):
    """Test creating context without copying to clipboard."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a file
        file_path = os.path.join(temp_dir, "file.txt")
        with open(file_path, "w") as f:
            f.write("test content")
        
        # Create a ContextCreator instance
        creator = ContextCreator(
            temp_dir,
            file_filter=lambda path: True,
        )
        
        # Create context without copying to clipboard
        context = creator.create_context(copy_to_clipboard=False)
        
        # Check that the context contains the file
        assert "file.txt:" in context
        assert "```text" in context
        assert "test content" in context
        
        # Check that the context was not copied to the clipboard
        mock_copy.assert_not_called() 