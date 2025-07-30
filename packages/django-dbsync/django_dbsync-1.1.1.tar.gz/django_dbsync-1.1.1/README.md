# Django DB Sync

**Django DB Sync** is a powerful, intelligent database synchronization tool designed specifically for Django projects. It automatically detects and resolves schema differences between your Django models and database tables, eliminating the need for manual migrations in many scenarios.

## Why Django DB Sync?

Unlike Django's built-in migrations system, Django DB Sync works by analyzing the current state of your database and comparing it directly with your Django models. This approach is particularly valuable when:

- Working with legacy databases that weren't created with Django
- Dealing with databases that have been manually modified
- Syncing schemas across different environments
- Cleaning up orphaned tables and unused columns
- Requiring granular control over database schema changes

## Key Features

- Multi-Database Support: Works seamlessly with MySQL, PostgreSQL, SQLite, and Oracle
- Intelligent Schema Detection: Automatically compares Django models with actual database schema
- Safety First: Built-in dry-run mode and backup creation before making changes
- Comprehensive Reporting: Detailed HTML reports and colored terminal output
- Orphaned Table Management: Identifies and manages tables without corresponding Django models
- Smart Field Mapping: Intelligent mapping between Django field types and database column types
- Constraint Handling: Proper management of foreign keys, indexes, and other constraints
- Beautiful Interface: Colored terminal output with progress indicators and status updates

## 🛠️ Core Capabilities

1. **Table Management**: Create, rename, and manage database tables
2. **Column Operations**: Add, modify, and remove columns with proper type mapping
3. **Constraint Handling**: Manage foreign keys, unique constraints, and indexes
4. **Data Preservation**: Safely modify schemas while preserving existing data
5. **Backup Integration**: Automatic backup creation before destructive operations
6. **Detailed Reporting**: Comprehensive logs and HTML reports of all operations

## 🔧 Technical Highlights

- **Database Agnostic**: Works with all major database backends supported by Django
- **Type-Safe Operations**: Intelligent field type mapping and validation
- **Transaction Safety**: All operations wrapped in database transactions
- **Extensible Architecture**: Modular design for easy customization and extension
- **Production Ready**: Thoroughly tested with comprehensive error handling

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
# Basic sync commands
python manage.py dbsync  # Sync default database
python manage.py dbsync --database=secondary  # Sync specific database
python manage.py dbsync --dry-run  # Show changes without applying
python manage.py dbsync --auto-approve  # Auto-approve all changes (dangerous!)
python manage.py dbsync --drop-orphaned  # Drop orphaned tables (dangerous!)
```

### Advanced Options
```bash
# App management
python manage.py dbsync --exclude-apps admin auth contenttypes  # Exclude specific apps
python manage.py dbsync --include-apps myapp otherapp  # Include only specific apps

# Backup and reporting
python manage.py dbsync --backup  # Create backup before sync
python manage.py dbsync --report json  # Generate JSON report
python manage.py dbsync --report html  # Generate HTML report
python manage.py dbsync --report both  # Generate both JSON and HTML reports

# Safety checks
python manage.py dbsync --drop-orphaned --dry-run  # Check what would be dropped
python manage.py dbsync --suggest-manual-commands  # Show manual SQL commands
python manage.py dbsync --generate-orphaned-models  # Generate models for orphaned tables
```

### Database Check
```bash
# Database checking commands
python manage.py dbcheck  # Check database schema
python manage.py dbcheck --database=secondary  # Check specific database
python manage.py dbcheck --table=my_table  # Show specific table details
python manage.py dbcheck --compare-models  # Compare with Django models
python manage.py dbcheck --check-case-mismatches  # Check for case mismatches
python manage.py dbcheck --check-name-conflicts  # Check for name conflicts
python manage.py dbcheck --verbose  # Show detailed information
python manage.py dbcheck --fix  # Attempt to fix issues automatically
python manage.py dbcheck --include-apps=app1,app2  # Check specific apps only
python manage.py dbcheck --include-tables=table1,table2  # Check specific tables only
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
    'AUTO_FIX_TABLE_CASE': True,  # Automatically fix table name case mismatches
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
- FileField, ImageField
- ForeignKey, OneToOneField, ManyToManyField

## Table Name Case Handling

Django-dbsync automatically detects and handles table name case mismatches between your Django models and the database. This is common when:

- Your model has `db_table = 'abcd'` but the database table is `ABCD`
- Database systems are case-insensitive but Django models use specific casing
- Tables were created with different naming conventions

### Automatic Case Fixing

By default, the tool will automatically fix case-only mismatches (when `AUTO_FIX_TABLE_CASE = True`):

```bash
# The tool will automatically rename 'ABCD' to 'abcd'
python manage.py dbsync
```

### Manual Control

To disable automatic case fixing and get prompted for each rename:

```python
DJANGO_DBSYNC = {
    'AUTO_FIX_TABLE_CASE': False,
}
```

### Checking for Case Mismatches

To check for table name case mismatches without fixing them:

```bash
python manage.py dbcheck --check-case-mismatches
```

This will show you all mismatches found and provide guidance on how to fix them.

### Manual SQL Commands for Table Renames

When table name conflicts are detected, you can get manual SQL commands to resolve them:

```bash
python manage.py dbsync --dry-run --suggest-manual-commands
```

This will show you the exact SQL commands needed to rename tables manually:

```
============================================================
🔧 MANUAL SQL COMMANDS FOR TABLE RENAMES
============================================================
The following SQL commands can be run manually to rename tables:

1. MySQL case-insensitive conflict resolution: 'publisher_detail2' → 'Publisher_detail2'
   SQL: RENAME TABLE `publisher_detail2` TO `Publisher_detail2`;

💡 Instructions:
   1. Connect to your database using your preferred SQL client
   2. Run the commands above one by one
   3. Run 'python manage.py dbsync' again to complete the sync
   4. Make sure to backup your database before running these commands!
```

This gives you full control over table renaming operations while ensuring data safety.

**Note:** Manual SQL commands are automatically displayed in dry-run mode, so you don't need the `--suggest-manual-commands` flag anymore.

### Generating Models for Orphaned Tables

When orphaned tables are found, you can generate Django models for them:

```bash
python manage.py dbsync --dry-run --generate-orphaned-models
```

This creates a Python file with Django models for all orphaned tables:

```python
# Django Models for Orphaned Tables
# Generated by django-dbsync on 2025-07-28 10:34:31
# 
# Instructions:
# 1. Copy the models you want to keep to your Django app's models.py
# 2. Remove the 'managed = False' line if you want Django to manage the table
# 3. Update the Meta class as needed
# 4. Run 'python manage.py makemigrations' and 'python manage.py migrate'

from django.db import models

# Table: publisher
# Rows: 0, Size: 0.02 MB
class Publisher(models.Model):
    """
    Auto-generated model for table 'publisher'
    Generated by django-dbsync
    """
    name = models.CharField(max_length=100, null=False, blank=False)
    website = models.CharField(max_length=200, null=False, blank=False)
    created_at = models.DateTimeField(null=False, blank=False)

    class Meta:
        db_table = 'publisher'
        managed = False  # Django won't manage this table

    def __str__(self):
        return f'Publisher(id={self.id})'
```

**Benefits:**
- **Easy retention**: Copy models to keep orphaned tables
- **Auto-generated**: No manual model writing needed
- **Safe**: Uses `managed = False` by default
- **Complete**: Includes all field types and constraints

### Table Name Conflicts

Sometimes databases can have both lowercase and uppercase versions of the same table name (e.g., `publisher` and `Publisher`). This can cause issues with table renaming operations.

To check for table name conflicts:

```bash
python manage.py dbcheck --check-name-conflicts
```

This will identify any tables that have case conflicts and provide guidance on how to resolve them.

**Example conflict scenario:**
- Database has both `publisher` and `Publisher` tables
- Django model expects `Publisher` 
- The tool will detect this conflict and avoid the rename operation
- You'll need to manually resolve the conflict before syncing

## Example Output

```
Django Database Sync v1.0.2
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


## Support

- GitHub Issues: https://github.com/Lovedazzell/db_sync/issues
- Documentation: https://django-dbsync.readthedocs.io/
- Email: lovepreetdazzell@gmail.com
