"""Tests for the FileFilter class."""

import os
import tempfile
from pathlib import Path

import pytest

from context_creator.file_filter import FileFilter


def test_is_text_file():
    """Test checking if a file is a text file."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a text file
        text_file = os.path.join(temp_dir, "text.txt")
        with open(text_file, "w") as f:
            f.write("This is a text file")
        
        # Create a binary file
        binary_file = os.path.join(temp_dir, "binary.bin")
        with open(binary_file, "wb") as f:
            f.write(b"\x00\x01\x02\x03")
        
        # Create a FileFilter instance
        file_filter = FileFilter(temp_dir)
        
        # Check if the files are text files
        assert file_filter.is_text_file(Path(text_file))
        assert not file_filter.is_text_file(Path(binary_file))


def test_is_in_excluded_dir():
    """Test checking if a path is inside an excluded directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a .git directory
        git_dir = os.path.join(temp_dir, ".git")
        os.makedirs(git_dir)
        
        # Create a file in the .git directory
        git_file = os.path.join(git_dir, "HEAD")
        with open(git_file, "w") as f:
            f.write("ref: refs/heads/main")
        
        # Create a file outside the .git directory
        normal_file = os.path.join(temp_dir, "file.txt")
        with open(normal_file, "w") as f:
            f.write("This is a normal file")
        
        # Create a FileFilter instance
        file_filter = FileFilter(temp_dir)
        
        # Check if the files are in excluded directories
        assert file_filter.is_in_excluded_dir(Path(git_file))
        assert not file_filter.is_in_excluded_dir(Path(normal_file))


def test_is_excluded_file():
    """Test checking if a file is in the list of excluded files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a .gitignore file
        gitignore_file = os.path.join(temp_dir, ".gitignore")
        with open(gitignore_file, "w") as f:
            f.write("*.log\n*.tmp\n")
        
        # Create a normal file
        normal_file = os.path.join(temp_dir, "file.txt")
        with open(normal_file, "w") as f:
            f.write("This is a normal file")
        
        # Create a FileFilter instance
        file_filter = FileFilter(temp_dir)
        
        # Check if the files are excluded
        assert file_filter.is_excluded_file(Path(gitignore_file))
        assert not file_filter.is_excluded_file(Path(normal_file))


def test_create_filter():
    """Test creating a filter function."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a .git directory
        git_dir = os.path.join(temp_dir, ".git")
        os.makedirs(git_dir)
        
        # Create a file in the .git directory
        git_file = os.path.join(git_dir, "HEAD")
        with open(git_file, "w") as f:
            f.write("ref: refs/heads/main")
        
        # Create a .gitignore file
        gitignore_file = os.path.join(temp_dir, ".gitignore")
        with open(gitignore_file, "w") as f:
            f.write("*.log\n*.tmp\n")
        
        # Create a text file
        text_file = os.path.join(temp_dir, "text.txt")
        with open(text_file, "w") as f:
            f.write("This is a text file")
        
        # Create a binary file
        binary_file = os.path.join(temp_dir, "binary.bin")
        with open(binary_file, "wb") as f:
            f.write(b"\x00\x01\x02\x03")
        
        # Create a FileFilter instance
        file_filter = FileFilter(temp_dir)
        filter_func = file_filter.create_filter()
        
        # Check if the files pass the filter
        assert filter_func(Path(text_file))
        assert not filter_func(Path(binary_file))
        assert not filter_func(Path(git_file))
        assert not filter_func(Path(gitignore_file))


def test_create_filter_with_exclude_patterns():
    """Test creating a filter function with exclude patterns."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create some files
        text_file = os.path.join(temp_dir, "text.txt")
        log_file = os.path.join(temp_dir, "log.log")
        
        with open(text_file, "w") as f:
            f.write("This is a text file")
        with open(log_file, "w") as f:
            f.write("This is a log file")
        
        # Create a FileFilter instance with exclude patterns
        file_filter = FileFilter(
            temp_dir,
            additional_exclude_patterns=["*.log"],
        )
        filter_func = file_filter.create_filter()
        
        # Check if the files pass the filter
        assert filter_func(Path(text_file))
        assert not filter_func(Path(log_file)) 