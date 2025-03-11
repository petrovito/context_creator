"""Tests for the main module."""

import os
import sys
import tempfile
from unittest.mock import patch, ANY

import pytest

from context_creator.main import main, parse_args


def test_parse_args():
    """Test parsing command-line arguments."""
    # Test with default arguments
    args = parse_args([])
    assert args.directory == "."
    assert not args.no_gitignore
    assert args.exclude == []
    assert not args.no_clipboard
    assert args.output is None
    
    # Test with custom arguments
    args = parse_args([
        "/path/to/dir",
        "--no-gitignore",
        "--exclude", "*.log",
        "--exclude", "*.tmp",
        "--no-clipboard",
        "--output", "output.txt",
    ])
    assert args.directory == "/path/to/dir"
    assert args.no_gitignore
    assert args.exclude == ["*.log", "*.tmp"]
    assert args.no_clipboard
    assert args.output == "output.txt"


@patch("context_creator.main.ContextCreator")
def test_main_success(mock_context_creator):
    """Test the main function with successful execution."""
    # Mock the ContextCreator instance
    mock_instance = mock_context_creator.return_value
    mock_instance.create_context.return_value = "test context"
    
    # Call the main function
    exit_code = main(["--no-clipboard"])
    
    # Check that the main function returned success
    assert exit_code == 0
    
    # Check that ContextCreator was called with the correct arguments
    mock_context_creator.assert_called_once()
    mock_instance.create_context.assert_called_once_with(copy_to_clipboard=False)


@patch("context_creator.main.ContextCreator")
def test_main_with_output_file(mock_context_creator):
    """Test the main function with an output file."""
    with tempfile.TemporaryDirectory() as temp_dir:
        output_file = os.path.join(temp_dir, "output.txt")
        
        # Mock the ContextCreator instance
        mock_instance = mock_context_creator.return_value
        mock_instance.create_context.return_value = "test context"
        
        # Call the main function with an output file
        with patch("builtins.print") as mock_print:
            exit_code = main(["--output", output_file])
        
        # Check that the main function returned success
        assert exit_code == 0
        
        # Check that the output file was created with the correct content
        with open(output_file, "r") as f:
            content = f.read()
        assert content == "test context"
        
        # Check that a message was printed
        mock_print.assert_called_once_with(f"Context written to {output_file}")


@patch("context_creator.main.ContextCreator")
def test_main_error(mock_context_creator):
    """Test the main function with an error."""
    # Mock the ContextCreator instance to raise an exception
    mock_context_creator.side_effect = Exception("Test error")
    
    # Call the main function
    with patch("builtins.print") as mock_print:
        exit_code = main([])
    
    # Check that the main function returned an error code
    assert exit_code == 1
    
    # Check that an error message was printed
    mock_print.assert_called_once_with("Error: Test error", file=ANY) 