"""Main entry point for the Context Creator command-line tool."""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from context_creator.context_creator import ContextCreator
from context_creator.file_filter import FileFilter
from context_creator.types import PathLike


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """
    Parse command-line arguments.

    Args:
        args: Command-line arguments. If None, sys.argv[1:] is used.

    Returns:
        An argparse.Namespace object containing the parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="Create context for LLMs from a development project."
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="The directory to scan (default: current directory)",
    )
    parser.add_argument(
        "--no-gitignore",
        action="store_true",
        help="Ignore .gitignore files",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="Additional patterns to exclude (can be specified multiple times)",
    )
    parser.add_argument(
        "--no-clipboard",
        action="store_true",
        help="Don't copy the context to the clipboard",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output file (default: stdout if --no-clipboard is specified)",
    )
    
    return parser.parse_args(args)


def main(args: Optional[List[str]] = None) -> int:
    """
    Main entry point for the command-line tool.

    Args:
        args: Command-line arguments. If None, sys.argv[1:] is used.

    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    parsed_args = parse_args(args)
    
    try:
        # Create a file filter
        file_filter = FileFilter(
            parsed_args.directory,
            use_gitignore=not parsed_args.no_gitignore,
            additional_exclude_patterns=parsed_args.exclude,
        ).create_filter()
        
        # Create a context creator
        context_creator = ContextCreator(
            root_dir=parsed_args.directory,
            file_filter=file_filter,
        )
        
        # Create context
        context = context_creator.create_context(
            copy_to_clipboard=not parsed_args.no_clipboard,
        )
        
        # Output to file if requested
        if parsed_args.output:
            with open(parsed_args.output, "w", encoding="utf-8") as f:
                f.write(context)
            print(f"Context written to {parsed_args.output}")
        # Output to stdout if no clipboard and no output file
        elif parsed_args.no_clipboard:
            print(context)
            
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main()) 