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
        # Create excluded directories
        excluded_dirs = [
            os.path.join(temp_dir, ".git"),
            os.path.join(temp_dir, ".vscode"),
        ]
        
        for dir_path in excluded_dirs:
            os.makedirs(dir_path)
            
            # Create a file in each excluded directory
            file_path = os.path.join(dir_path, "file.txt")
            with open(file_path, "w") as f:
                f.write("Test file")
        
        # Create a file in a normal directory
        normal_dir = os.path.join(temp_dir, "normal_dir")
        os.makedirs(normal_dir)
        normal_file = os.path.join(normal_dir, "file.txt")
        with open(normal_file, "w") as f:
            f.write("This is a normal file")
        
        # Create a FileFilter instance
        file_filter = FileFilter(temp_dir)
        
        # Check if the files are in excluded directories
        for dir_path in excluded_dirs:
            file_path = os.path.join(dir_path, "file.txt")
            assert file_filter.is_in_excluded_dir(Path(file_path))
            
        # Check that the normal file is not in an excluded directory
        assert not file_filter.is_in_excluded_dir(Path(normal_file))


def test_is_excluded_file():
    """Test checking if a file is in the list of excluded files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create excluded files
        excluded_files = [
            ".gitignore",
            "Cargo.lock",
            "package-lock.json",
            "yarn.lock",
            ".editorconfig",
            ".prettierrc",
            "tsconfig.json",
        ]
        
        file_paths = {}
        for filename in excluded_files:
            file_path = os.path.join(temp_dir, filename)
            with open(file_path, "w") as f:
                f.write(f"Content of {filename}")
            file_paths[filename] = file_path
        
        # Create files that match wildcard patterns
        wildcard_files = {
            "test.min.js": "Minified JavaScript",
            "styles.min.css": "Minified CSS",
            "source.map": "Source map file",
        }
        
        for filename, content in wildcard_files.items():
            file_path = os.path.join(temp_dir, filename)
            with open(file_path, "w") as f:
                f.write(content)
            file_paths[filename] = file_path
        
        # Create a normal file
        normal_file = os.path.join(temp_dir, "normal.txt")
        with open(normal_file, "w") as f:
            f.write("This is a normal file")
        
        # Create a FileFilter instance
        file_filter = FileFilter(temp_dir)
        
        # Check excluded files
        for filename, file_path in file_paths.items():
            assert file_filter.is_excluded_file(Path(file_path)), f"{filename} should be excluded"
        
        # Check that the normal file is not excluded
        assert not file_filter.is_excluded_file(Path(normal_file))


def test_create_filter():
    """Test creating a filter function."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a .git directory with a file
        git_dir = os.path.join(temp_dir, ".git")
        os.makedirs(git_dir)
        git_file = os.path.join(git_dir, "HEAD")
        with open(git_file, "w") as f:
            f.write("ref: refs/heads/main")
        
        # Create excluded files
        excluded_files = {
            ".gitignore": "*.log\n*.tmp\n",
            "Cargo.lock": "Cargo lock file content",
            "package-lock.json": "{ \"name\": \"test\", \"version\": \"1.0.0\" }",
            "tsconfig.json": "{ \"compilerOptions\": {} }",
        }
        
        for filename, content in excluded_files.items():
            file_path = os.path.join(temp_dir, filename)
            with open(file_path, "w") as f:
                f.write(content)
        
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
        assert filter_func(Path(text_file)), "Text file should pass the filter"
        assert not filter_func(Path(binary_file)), "Binary file should not pass the filter"
        assert not filter_func(Path(git_file)), "Git file should not pass the filter"
        
        # Check excluded files
        for filename in excluded_files:
            file_path = os.path.join(temp_dir, filename)
            assert not filter_func(Path(file_path)), f"{filename} should not pass the filter"


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
        assert filter_func(Path(text_file)), "Text file should pass the filter"
        assert not filter_func(Path(log_file)), "Log file should not pass the filter" 