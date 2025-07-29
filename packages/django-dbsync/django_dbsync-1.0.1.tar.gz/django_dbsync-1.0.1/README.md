"""
# Django DB Sync

Advanced Django database synchronization tool with multi-database support.

## Features

- 🔄 **Multi-Database Support**: Sync different databases with custom configurations
- 🎯 **Smart Detection**: Automatically detects schema differences between models and database
- 🛡️ **Safety First**: Dry-run mode, confirmations, and backup support
- 📊 **Detailed Reports**: JSON and HTML reports with comprehensive sync information
- 🎨 **Colored Output**: Beautiful terminal output with progress indicators
- 🔍 **Orphaned Tables**: Identifies tables in database without corresponding models
- ⚡ **Field Mapping**: Supports all Django field types across MySQL, PostgreSQL, and SQLite
- 🔧 **Flexible Configuration**: Extensive settings for customizing sync behavior

## Installation

```bash
pip install django-dbsync
```

Add to your Django settings:

```python
INSTALLED_APPS = [
    # ... other apps
    'django_dbsync',
]

# Optional: Configure django-dbsync
DJANGO_DBSYNC = {
    'DEFAULT_DATABASE': 'default',
    'AUTO_CREATE_TABLES': True,
    'AUTO_ADD_COLUMNS': True,
    'AUTO_DROP_COLUMNS': False,
    'EXCLUDE_APPS': ['admin', 'contenttypes', 'sessions'],
    'COLORED_OUTPUT': True,
    'SHOW_ORPHANED_TABLES': True,
}
```

## Usage

### Basic Sync
```bash
# Sync default database
python manage.py dbsync

# Sync specific database
python manage.py dbsync --database=secondary

# Dry run (show changes without applying)
python manage.py dbsync --dry-run

# Auto-approve all changes (dangerous!)
python manage.py dbsync --auto-approve

# Drop orphaned tables (dangerous!)
python manage.py dbsync --drop-orphaned 
```

### Advanced Options
```bash
# Exclude specific apps
python manage.py dbsync --exclude-apps admin auth contenttypes

# Include only specific apps
python manage.py dbsync --include-apps myapp otherapp

# Create backup before sync
python manage.py dbsync --backup

# Generate detailed report
python manage.py dbsync --report json
python manage.py dbsync --report html
python manage.py dbsync --report both

# Drop orphaned tables (dry run)
python manage.py dbsync --drop-orphaned --dry-run
```

### Database Check
```bash
# Check database schema
python manage.py dbcheck

# Check specific database
python manage.py dbcheck --database=secondary

# Show specific table details
python manage.py dbcheck --table=my_table

# Compare with Django models
python manage.py dbcheck --compare-models


```

## Configuration

### Database Settings

Support for multiple databases: 

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'main_db',
        'USER': 'user',
        'PASSWORD': 'pass',
        'HOST': 'localhost',
    },
    'analytics': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'analytics_db',
        'USER': 'user',
        'PASSWORD': 'pass',
        'HOST': 'localhost',
    }
}

# Sync configuration per database
DJANGO_DBSYNC = {
    'CUSTOM_DATABASES': {
        'analytics': {
            'AUTO_DROP_COLUMNS': True,
            'EXCLUDE_APPS': ['admin'],
        }
    }
}
```

### Complete Settings Reference

```python
DJANGO_DBSYNC = {
    # Database configuration
    'DEFAULT_DATABASE': 'default',
    'CUSTOM_DATABASES': None,
    
    # Sync behavior
    'AUTO_CREATE_TABLES': True,
    'AUTO_ADD_COLUMNS': True,
    'AUTO_DROP_COLUMNS': False,
    'AUTO_RENAME_TABLES': False,
    'BACKUP_BEFORE_SYNC': True,
    
    # Output settings
    'COLORED_OUTPUT': True,
    'VERBOSE_LOGGING': True,
    'SHOW_PROGRESS': True,
    
    # Safety settings
    'EXCLUDE_APPS': ['sessions', 'admin', 'contenttypes'],
    'EXCLUDE_TABLES': [],
    'DRY_RUN_MODE': False,
    
    # Report settings
    'GENERATE_HTML_REPORT': False,
    'REPORT_OUTPUT_DIR': 'dbsync_reports/',
    'SHOW_ORPHANED_TABLES': True,
}
```

## Supported Field Types

All Django field types are supported across MySQL, PostgreSQL, and SQLite:

- AutoField, BigAutoField
- CharField, TextField, EmailField, URLField, SlugField
- IntegerField, BigIntegerField, SmallIntegerField
- PositiveIntegerField, PositiveSmallIntegerField
- FloatField, DecimalField
- BooleanField
- DateField, DateTimeField, TimeField
- UUIDField, JSONField
- ForeignKey, OneToOneField

## Example Output

```
Django Database Sync v1.0.0
==================================================
Starting synchronization...

✅ myapp.User
   - Added column 'phone' to 'users'
   - Modified column 'email' in 'users'

⚠️  myapp.Order
   - Table 'orders_old' renamed to 'orders'
   - Extra column 'temp_field' in 'orders' (kept)

❌ myapp.Product
   - Failed to add column 'description'

⚠️  Orphaned Tables (2 found):
🗃️  old_backup_table - 1,247 rows, 2.45 MB
🗃️  temp_migration - 0 rows, 0.01 MB

Synchronization completed!
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License. See LICENSE file for details.

## Support

- GitHub Issues: https://github.com/Lovedazzell/db_sync/issues
- Documentation: https://django-dbsync.readthedocs.io/
- Email: lovedzzell@gmail.com
"""