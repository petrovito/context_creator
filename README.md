# Context Creator

A command-line tool that creates context for LLMs from a development project.

## Features

- Recursively scans a directory for text files
- Respects `.gitignore` rules to exclude unwanted files
- Formats file contents with path and syntax highlighting markers
- Copies the generated context to the system clipboard

## Installation

```bash
# Clone the repository
git clone https://github.com/petrovito/context_creator.git
cd context_creator

# Install the package
pip install -e .
```

## Usage

```bash
# Basic usage - process the current directory
context-creator .

# Process a specific directory
context-creator /path/to/project

# Show help
context-creator --help
```

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black context_creator tests
isort context_creator tests
```

## License

MIT 