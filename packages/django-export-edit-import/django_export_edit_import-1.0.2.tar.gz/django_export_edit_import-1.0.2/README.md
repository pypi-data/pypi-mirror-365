# Django Export Edit Import

A reusable Django app that enables export, edit and import (Excel) workflow for Django models. This package provides a seamless way to export model data to Excel files, allow external editing, and import the modified data back into your Django application.

## Features

- Export Django model data to Excel files
- Track export/import operations with detailed status information
- Handle import errors gracefully with error reporting
- Support for bulk operations (create, update, delete)
- Built-in file generation status tracking
- Integration with Celery for background processing
- Comprehensive error handling and logging

## Quick Start

### Installation

Install the package using pip:

```bash
pip install django-export-edit-import
```

Or if installing from source:

```bash
git clone https://your.git.server/django-export-edit-import
cd django-export-edit-import
pip install -e .
```

### Django Configuration

Add the app to your Django project's `INSTALLED_APPS`:

```python
# settings.py
INSTALLED_APPS = [
    # ... your other apps
    'export_edit_import',
    # ... rest of your apps
]
```

### Database Setup

Run migrations to create the necessary database tables:

```bash
# Generate migrations (if needed)
python manage.py makemigrations export_edit_import

# Apply migrations
python manage.py migrate
```

### Dependencies

This package requires the following dependencies:
- Django >= 4.2
- pandas >= 2.0
- openpyxl >= 3.1

## Basic Usage

### Exporting Data

```python
from export_edit_import.models import GeneratedExportFile
from django.contrib.contenttypes.models import ContentType
from myapp.models import MyModel

# Create an export file
content_type = ContentType.objects.get_for_model(MyModel)
export_file = GeneratedExportFile.objects.create(
    related_model_type=content_type
)

# Process the export (typically done in a background task)
# ... your export logic here
```

### Importing Data

```python
from export_edit_import.models import GeneratedImportFile
from django.contrib.contenttypes.models import ContentType

# Create an import file
import_file = GeneratedImportFile.objects.create(
    related_model_type=content_type,
    file=uploaded_file
)

# Process the import (typically done in a background task)
# ... your import logic here
```

## Models Overview

### GeneratedFile (Abstract Base)
- Base class for tracking file generation operations
- Includes status tracking, error handling, and task management
- Supports integration with Celery for background processing

### GeneratedExportFile
- Tracks Excel export operations
- Provides methods to check if export files are up-to-date
- Handles file reuse logic to avoid unnecessary regenerations

### GeneratedImportFile
- Tracks Excel import operations
- Provides detailed statistics (created, updated, deleted rows)
- Handles error file generation for failed import rows

## File Status Options

- `PENDING`: Operation is queued or in progress
- `COMPLETED`: Operation completed successfully
- `FAILED`: Operation failed with errors
- `COMPLETED_WITH_ERRORS`: Operation completed but with some errors

## Migration Commands

### Initial Setup
```bash
python manage.py makemigrations export_edit_import
python manage.py migrate
```

### After Updates
```bash
python manage.py makemigrations
python manage.py migrate
```

## Upgrade Path

### From Development to 1.0.0
This is the initial release. No upgrade path needed.

### Future Versions
When upgrading to future versions:
1. Review the changelog below
2. Update your requirements/dependencies
3. Run `pip install -U django-export-edit-import`
4. Run `python manage.py makemigrations`
5. Run `python manage.py migrate`
6. Test your implementation thoroughly

## Changelog

### v1.0.0 (Initial Release)
- ✨ Initial release of django-export-edit-import
- 📦 Core export/import functionality
- 🗄️ Database models for tracking operations
- 📊 Support for Excel file processing
- 🔄 Status tracking and error handling
- 📋 Integration with Django's ContentTypes framework
- ⚡ Background task support preparation

### Future Releases
- v1.1.0 - Enhanced error reporting and validation
- v1.2.0 - Additional file format support
- v2.0.0 - Breaking changes and major improvements

---

## Development

### Requirements
- Python >= 3.9
- Django >= 4.2

### Development Setup
```bash
pip install -e .[dev]
```

### Running Tests
```bash
pytest
```

## License

MIT License. See LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
