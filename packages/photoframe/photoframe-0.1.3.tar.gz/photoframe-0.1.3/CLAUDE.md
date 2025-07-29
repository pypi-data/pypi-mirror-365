# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Watermarker is a Python CLI tool for adding lossless watermarks to photos with support for multiple templates and automatic orientation detection. The tool uses uv for package management and follows a modular architecture with Click-based CLI.

## Development Commands

### Setup and Installation
```bash
# Install dependencies and sync environment
uv sync

# Run the CLI tool locally
uv run watermarker --help
uv run watermarker add photo.jpg --template date
uv run watermarker info photo.jpg
```

### Testing
```bash
# Run all tests
uv run pytest

# Run tests with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_templates.py

# Run specific test method
uv run pytest tests/test_templates.py::TestDateTemplate::test_generate_text_with_exif_date
```

### Code Quality
```bash
# Format code with black
uv run black src/

# Sort imports with isort
uv run isort src/

# Run linting with flake8
uv run flake8 src/
```

## Architecture Overview

### Core Components

**CLI Structure**: Uses Click with a group command pattern:
- `watermarker` - Main group command
  - `add` - Add watermark subcommand (main functionality)
  - `info` - Display image EXIF information

**Template System**: Abstract base class pattern in `src/watermarker/templates/`:
- `BaseTemplate` - Abstract base defining the template interface
- `DateTemplate` - Basic date watermarks from EXIF data
- `BabyTemplate` - Age calculation for baby photos requiring birth date
- `CameraTemplate` - Camera parameters display (Leica-style)

**Image Processing Pipeline**:
1. `ImageProcessor` loads image and handles EXIF orientation
2. `ExifReader` extracts metadata (datetime, camera info, settings)
3. Template generates watermark text based on EXIF data
4. `ImageProcessor` renders watermark and saves losslessly

### Key Design Patterns

**Template Registration**: Templates are registered in `cli.py:get_template()` function with a simple dictionary mapping. To add new templates:
1. Create template class inheriting from `BaseTemplate`
2. Implement `generate_text()` and `validate_requirements()` methods
3. Add to `template_classes` dict in `get_template()`

**EXIF Data Flow**: 
- `ExifReader` uses dual libraries (exifread + PIL) for robustness
- EXIF data passed as standardized dict to templates
- Templates validate required data availability before rendering

**Error Handling Strategy**:
- Input validation at CLI level (file format, existence)
- Template-level validation for required EXIF data
- Graceful fallbacks (current date if no EXIF datetime)

## Template Development

### Creating New Templates

1. Inherit from `BaseTemplate` in `src/watermarker/templates/`
2. Implement required abstract methods:
   ```python
   def generate_text(self, exif_data: Dict[str, Any], **kwargs) -> str:
       """Generate watermark text from EXIF data"""
   
   def validate_requirements(self, exif_data: Dict[str, Any], **kwargs) -> bool:
       """Check if template can run with available data"""
   ```

3. Register in `cli.py:get_template()` function
4. Add CLI options if needed (see baby template's `--baby-birth-date`)

### EXIF Data Structure

Templates receive standardized EXIF data dict:
```python
{
    'datetime': datetime object or None,
    'camera_info': {'make': str, 'model': str},
    'lens_info': {'lens_model': str, 'focal_length': str},  
    'settings': {'aperture': str, 'shutter_speed': str, 'iso': str}
}
```

## Image Processing Details

**Supported Formats**: JPEG, PNG, TIFF, BMP, WebP (defined in `core/utils.py:SUPPORTED_FORMATS`)

**Quality Preservation**: 
- EXIF data preserved during processing
- High-quality save parameters per format
- No re-compression unless necessary

**Positioning Algorithm**:
- Relative positioning (3% margin from edges)
- Auto-scaling based on image dimensions
- Orientation-aware text placement

## Testing Strategy

**Test Organization**:
- Template logic tested in isolation with mock EXIF data
- Focus on text generation and validation logic
- No actual image rendering in unit tests (too slow/complex)

**Test Data Patterns**:
```python
# Standard EXIF data structure for tests
exif_data = {
    'datetime': datetime(2024, 5, 15, 14, 30, 0),
    'camera_info': {'make': 'Canon', 'model': 'EOS R5'},
    # ...
}
```

## CLI Design Principles

**Command Structure**: Two-level commands for clarity:
- Main functionality in `add` subcommand
- Utility functionality in `info` subcommand
- Allows for future expansion (batch processing, config management)

**Parameter Validation**: Click handles type validation, custom validation in template classes

**Error Messages**: Chinese language error messages for user-facing errors, English for developer errors

## Dependencies and Constraints

**Core Dependencies**:
- `click>=8.1.0` - CLI framework
- `Pillow>=10.0.0` - Image processing  
- `exifread>=3.0.0` - EXIF data extraction
- `python-dateutil>=2.8.0` - Date handling for baby template

**Python Version**: Requires Python >=3.12 (uses modern type hints)

**Font Handling**: Falls back through multiple system font paths if bundled fonts unavailable

## Common Development Patterns

**Adding CLI Options**: Add to both `@click.option` decorators and function signature in `cli.py:add` command

**EXIF Fallbacks**: Always provide fallback behavior when EXIF data unavailable (see DateTemplate using current date)

**Template Validation**: Use `validate_requirements()` to fail fast rather than during rendering

**Path Handling**: Use `pathlib.Path` for cross-platform compatibility, convert to strings only at boundaries