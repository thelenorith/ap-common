# ap-common

[![Test](https://github.com/jewzaam/ap-common/workflows/Test/badge.svg)](https://github.com/jewzaam/ap-common/actions/workflows/test.yml)
[![Coverage](https://github.com/jewzaam/ap-common/workflows/Coverage%20Check/badge.svg)](https://github.com/jewzaam/ap-common/actions/workflows/coverage.yml)
[![Lint](https://github.com/jewzaam/ap-common/workflows/Lint/badge.svg)](https://github.com/jewzaam/ap-common/actions/workflows/lint.yml)
[![Format](https://github.com/jewzaam/ap-common/workflows/Format%20Check/badge.svg)](https://github.com/jewzaam/ap-common/actions/workflows/format.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Shared functionality package for astrophotography tools. Provides common utilities for FITS/XISF header reading, metadata normalization, file operations, and metadata extraction/filtering.

## Overview

This package extracts reusable functionality from astrophotography tools into a single installable package that can be shared across multiple projects. It provides:

- **FITS/XISF Header Reading**: Extract and parse headers from FITS and XISF files
- **Header Normalization**: Standardize header names and values across different formats
- **Metadata Extraction**: Load and enrich metadata from files and filenames
- **File Operations**: Move, copy, and manage files with directory creation
- **Utility Functions**: Environment variable replacement, string conversion, file finding

## Documentation

This tool is part of the astrophotography pipeline. For comprehensive documentation including workflow guides and integration with other tools, see:

- **[Pipeline Overview](https://github.com/jewzaam/ap-base/blob/main/docs/index.md)** - Full pipeline documentation
- **[Workflow Guide](https://github.com/jewzaam/ap-base/blob/main/docs/workflow.md)** - Detailed workflow with diagrams
- **[ap-common Reference](https://github.com/jewzaam/ap-base/blob/main/docs/tools/ap-common.md)** - API reference for this tool

## Installation

### Local Development (Editable Install)

```powershell
# In ap-common directory
pip install -e .
```

### Local Package Install

```powershell
# Build and install from local directory
cd ap-common
pip install .
```

### From Local Path (in other projects)

```toml
# In other project's pyproject.toml dependencies:
dependencies = [
    "ap-common @ file:///path/to/ap-common",
]
```

### From Git Repository

```toml
dependencies = [
    "ap-common @ git+https://github.com/yourusername/ap-common.git",
]
```

## Package Structure

```
ap_common/
├── __init__.py          # Package exports
├── fits.py              # FITS/XISF header reading
├── normalization.py     # Header normalization functions and data
├── filesystem.py        # File operations (move, copy, delete_empty_dirs)
├── metadata.py          # Metadata extraction and filtering
└── utils.py             # Utility functions
```

## Usage

### Basic Example

```python
from ap_common.fits import get_fits_headers
from ap_common.normalization import normalize_headers
from ap_common.metadata import get_filtered_metadata

# Read FITS headers
headers = get_fits_headers("image.fits", profileFromPath=True)

# Get filtered metadata
metadata = get_filtered_metadata(
    dirs=["/path/to/images"],
    filters={"type": "LIGHT", "camera": "DWARFIII"},
    profileFromPath=True
)
```

### Available Functions

#### FITS Header Reading (`ap_common.fits`)
- `get_fits_headers()` - Extract headers from FITS files
- `get_xisf_headers()` - Extract headers from XISF files
- `get_file_headers()` - Extract headers from filenames

#### Normalization (`ap_common.normalization`)
- `normalize_headers()` - Normalize a dictionary of headers
- `normalize_date()` - Normalize date strings
- `normalize_datetime()` - Normalize datetime strings
- `normalize_filterName()` - Normalize filter names
- `normalize_target_name()` - Extract target and panel from target name
- `normalize_filename()` - Construct normalized filenames from headers
- `FILTER_NORMALIZATION_DATA` - Normalization mapping dictionary
- `CONSTANT_NORMALIZATION_DATA` - Constant value mappings

#### Filesystem (`ap_common.filesystem`)
- `move_file()` - Move files with directory creation
- `copy_file()` - Copy files with directory creation
- `delete_empty_directories()` - Recursively delete empty directories

#### Metadata (`ap_common.metadata`)
- `get_metadata()` - Load metadata for files in directories
- `enrich_metadata()` - Enrich metadata by reading file headers
- `get_filtered_metadata()` - Load and filter metadata
- `filter_metadata()` - Filter metadata dictionary by criteria

#### Utilities (`ap_common.utils`)
- `replace_env_vars()` - Replace environment variable placeholders
- `camelCase()` - Convert strings to camelCase
- `get_filenames()` - Find files matching patterns

## Dependencies

- `astropy` - For FITS file reading
- `xisf==0.9.5` - For XISF file reading

## Project-Specific Configuration

Some functions accept project-specific parameters:

- `directory_accept` - The "accept" directory name (defaults to "accept")
- Date format overrides in normalization functions

Projects should pass their specific constants when calling these functions.

## Benefits

- ✅ Single source of truth for common functionality
- ✅ Easy to update - fix once, all tools benefit
- ✅ Version control - can pin specific versions
- ✅ Clean separation of concerns
- ✅ Easier testing of shared code
- ✅ Can publish to PyPI if desired

## Development

### Running Tests

Install development dependencies:
```powershell
pip install -e ".[dev]"
```

Run tests (choose one method):

**Option 1: Direct pytest (Windows-friendly)**
```powershell
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=ap_common --cov-report=html --cov-report=term
```

**Option 2: Using Make (requires make installation)**
```powershell
make test
make test-verbose
make test-coverage
```

**Installing Make on Windows 11:**

The easiest way to install make on Windows 11:

```powershell
winget install ezwinports.make
```

After installation, close and reopen your terminal, or refresh the environment:
```powershell
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
```

**Alternative methods:**
- **Chocolatey**: `choco install make`
- **MSYS2/MinGW**: Install MSYS2, then `pacman -S make`
- **WSL**: `sudo apt install make` (if using WSL)

Verify installation:
```powershell
make --version
```

## Testing

The package includes comprehensive unit tests covering all modules:
- `test_utils.py` - Utility function tests
- `test_normalization.py` - Header normalization tests
- `test_filesystem.py` - File operation tests
- `test_fits.py` - FITS/XISF header reading tests
- `test_metadata.py` - Metadata extraction and filtering tests

