"""Tests for the FileFilter class."""

import os
import tempfile
from pathlib import Path
import mimetypes
from unittest.mock import patch

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


def test_always_text_extensions():
    """Test that files with extensions in ALWAYS_TEXT_EXTENSIONS are recognized as text files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create files with extensions that should always be considered text
        test_extensions = [".rs", ".go", ".ts", ".jsx", ".vue", ".rb", ".php"]
        test_files = {}
        
        for ext in test_extensions:
            filename = f"test{ext}"
            file_path = os.path.join(temp_dir, filename)
            with open(file_path, "w") as f:
                f.write(f"Content of {filename}")
            test_files[ext] = file_path
        
        # Create a FileFilter instance
        file_filter = FileFilter(temp_dir)
        
        # Test each file with a mocked MIME type that would normally cause it to be rejected
        for ext, file_path in test_files.items():
            # Mock the mimetypes.guess_type to return a non-text MIME type
            with patch('mimetypes.guess_type', return_value=('application/octet-stream', None)):
                # The file should still be recognized as text because of its extension
                assert file_filter.is_text_file(Path(file_path)), f"File with extension {ext} should be recognized as text"


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


def test_create_filter_with_always_text_extensions():
    """Test that the filter function correctly handles files with extensions in ALWAYS_TEXT_EXTENSIONS."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create files with extensions that should always be considered text
        rust_file = os.path.join(temp_dir, "main.rs")
        go_file = os.path.join(temp_dir, "server.go")
        typescript_file = os.path.join(temp_dir, "app.ts")
        
        with open(rust_file, "w") as f:
            f.write("fn main() { println!(\"Hello, world!\"); }")
        with open(go_file, "w") as f:
            f.write("package main\n\nfunc main() { fmt.Println(\"Hello, world!\") }")
        with open(typescript_file, "w") as f:
            f.write("console.log('Hello, world!');")
        
        # Create a FileFilter instance
        file_filter = FileFilter(temp_dir)
        filter_func = file_filter.create_filter()
        
        # Mock the mimetypes.guess_type to return a non-text MIME type
        with patch('mimetypes.guess_type', return_value=('application/octet-stream', None)):
            # The files should still pass the filter because of their extensions
            assert filter_func(Path(rust_file)), "Rust file should pass the filter"
            assert filter_func(Path(go_file)), "Go file should pass the filter"
            assert filter_func(Path(typescript_file)), "TypeScript file should pass the filter" 