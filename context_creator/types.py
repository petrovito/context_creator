"""Type definitions for the Context Creator package."""

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Optional, Set, Union


@dataclass
class FileInfo:
    """Information about a file in the project."""

    path: Path
    relative_path: Path
    content: str
    file_type: str


# Type aliases
FilterFunction = Callable[[Path], bool]
PathLike = Union[str, Path]
FileTree = Dict[Path, List[Path]] 