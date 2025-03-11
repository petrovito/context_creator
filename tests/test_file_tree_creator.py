"""Tests for the FileTreeCreator class."""

import os
import tempfile
from pathlib import Path

import pytest

from context_creator.file_tree_creator import FileTreeCreator


def test_create_file_tree_empty_directory():
    """Test creating a file tree from an empty directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a FileTreeCreator instance
        creator = FileTreeCreator(temp_dir)
        
        # Create a file tree
        file_tree = creator.create_file_tree()
        
        # Check that the file tree contains only the root directory
        assert len(file_tree) == 1
        assert Path(temp_dir) in file_tree
        assert file_tree[Path(temp_dir)] == []


def test_create_file_tree_with_files():
    """Test creating a file tree from a directory with files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create some files
        file_paths = [
            os.path.join(temp_dir, "file1.txt"),
            os.path.join(temp_dir, "file2.py"),
            os.path.join(temp_dir, "file3.md"),
        ]
        for file_path in file_paths:
            with open(file_path, "w") as f:
                f.write("test content")
        
        # Create a FileTreeCreator instance
        creator = FileTreeCreator(temp_dir)
        
        # Create a file tree
        file_tree = creator.create_file_tree()
        
        # Check that the file tree contains the root directory and all files
        assert len(file_tree) == 1
        assert Path(temp_dir) in file_tree
        assert len(file_tree[Path(temp_dir)]) == 3
        assert set(str(p) for p in file_tree[Path(temp_dir)]) == set(file_paths)


def test_create_file_tree_with_subdirectories():
    """Test creating a file tree from a directory with subdirectories."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create some subdirectories
        subdir1 = os.path.join(temp_dir, "subdir1")
        subdir2 = os.path.join(temp_dir, "subdir2")
        os.makedirs(subdir1)
        os.makedirs(subdir2)
        
        # Create some files
        file_paths = [
            os.path.join(temp_dir, "file1.txt"),
            os.path.join(subdir1, "file2.py"),
            os.path.join(subdir2, "file3.md"),
        ]
        for file_path in file_paths:
            with open(file_path, "w") as f:
                f.write("test content")
        
        # Create a FileTreeCreator instance
        creator = FileTreeCreator(temp_dir)
        
        # Create a file tree
        file_tree = creator.create_file_tree()
        
        # Check that the file tree contains all directories and files
        assert len(file_tree) == 3
        assert Path(temp_dir) in file_tree
        assert Path(subdir1) in file_tree
        assert Path(subdir2) in file_tree
        assert len(file_tree[Path(temp_dir)]) == 1
        assert len(file_tree[Path(subdir1)]) == 1
        assert len(file_tree[Path(subdir2)]) == 1
        assert str(file_tree[Path(temp_dir)][0]) == file_paths[0]
        assert str(file_tree[Path(subdir1)][0]) == file_paths[1]
        assert str(file_tree[Path(subdir2)][0]) == file_paths[2]


def test_create_file_tree_nonexistent_directory():
    """Test creating a file tree from a nonexistent directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        nonexistent_dir = os.path.join(temp_dir, "nonexistent")
        
        # Check that creating a FileTreeCreator with a nonexistent directory raises an error
        with pytest.raises(FileNotFoundError):
            FileTreeCreator(nonexistent_dir)


def test_create_file_tree_file_as_input():
    """Test creating a file tree with a file as input."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a file
        file_path = os.path.join(temp_dir, "file.txt")
        with open(file_path, "w") as f:
            f.write("test content")
        
        # Check that creating a FileTreeCreator with a file as input raises an error
        with pytest.raises(NotADirectoryError):
            FileTreeCreator(file_path) 