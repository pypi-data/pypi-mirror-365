import logging
from datetime import datetime
from django.apps import apps
from django.db import connections, models, transaction
from django.conf import settings
import re

from .database_inspector import DatabaseInspector
from .field_mapper import FieldMapper
from .exceptions import SyncOperationError
from ..settings import get_setting

logger = logging.getLogger(__name__)

class SyncEngine:
    """Main synchronization engine for Django models and database"""
    
    def __init__(self, database_alias='default', dry_run=False, auto_approve=False):
        self.database_alias = database_alias
        self.dry_run = dry_run
        self.auto_approve = auto_approve
        self.excluded_apps = set(get_setting('EXCLUDE_APPS', []))
        self.included_apps = None
        self.results = {}
        self._no_restriction = False  # Flag for no-restriction mode
        self.manual_commands = []  # Store manual SQL commands
        
        # Initialize components
        self.inspector = DatabaseInspector(database_alias)
        self.field_mapper = FieldMapper(connections[database_alias].vendor)
        self.field_mapper.sync_engine = self
    
    def set_excluded_apps(self, apps_list):
        """Set apps to exclude from synchronization"""
        self.excluded_apps.update(apps_list)
    
    def set_included_apps(self, apps_list):
        """Set apps to include (only these will be synced)"""
        self.included_apps = set(apps_list)
    
    def set_exclude_table_patterns(self, patterns_list):
        """Set regex patterns for tables to exclude"""
        self._temp_exclude_table_patterns = patterns_list
        # Update field mapper if it exists
        if hasattr(self, 'field_mapper'):
            self.field_mapper.sync_engine = self
    
    def set_exclude_app_patterns(self, patterns_list):
        """Set regex patterns for apps to exclude"""
        self._temp_exclude_app_patterns = patterns_list
    
    def set_no_restriction(self, enabled=True):
        """Disable all exclusions and sync ALL Django tables (including auth, admin, sessions, etc.)"""
        if enabled:
            # Clear all exclusions
            self.excluded_apps = set()
            self.included_apps = None
            # Clear temporary patterns
            self._temp_exclude_app_patterns = []
            self._temp_exclude_table_patterns = []
            # Set flag for field mapper to ignore exclusions
            self._no_restriction = True
            if hasattr(self, 'field_mapper'):
                self.field_mapper._no_restriction = True
        else:
            # Restore default exclusions
            self.excluded_apps = set(get_setting('EXCLUDE_APPS', []))
            self._no_restriction = False
            if hasattr(self, 'field_mapper'):
                self.field_mapper._no_restriction = False
    
    def get_models_to_sync(self):
        """Get filtered list of models to synchronize"""
        import re
        
        models_list = []
        
        # If no-restriction mode is enabled, include ALL models
        if getattr(self, '_no_restriction', False):
            for app_config in apps.get_app_configs():
                for model in app_config.get_models():
                    models_list.append(model)
            return models_list
        
        # Normal filtering logic
        exclude_app_patterns = get_setting('EXCLUDE_APP_PATTERNS', [])
        
        # Add temporary patterns from command line
        if hasattr(self, '_temp_exclude_app_patterns') and self._temp_exclude_app_patterns:
            exclude_app_patterns.extend(self._temp_exclude_app_patterns)
        
        for app_config in apps.get_app_configs():
            app_label = app_config.label
            
            # Skip excluded apps (explicit list)
            if app_label in self.excluded_apps:
                continue
            
            # Skip apps matching regex patterns
            skip_app = False
            for pattern in exclude_app_patterns:
                try:
                    if re.match(pattern, app_label):
                        skip_app = True
                        break
                except re.error:
                    # Invalid regex pattern, skip it
                    continue
            
            if skip_app:
                continue
            
            # If included_apps is set, only include those
            if self.included_apps and app_label not in self.included_apps:
                continue
            
            try:
                for model in app_config.get_models():
                    models_list.append(model)
            except Exception as e:
                error_message = str(e)
                logger.error(f"Error loading models from app '{app_label}': {error_message}")
                
                # Handle specific Django model errors
                if "can't have more than one auto-generated field" in error_message:
                    suggestion = f"""
🔧 DJANGO MODEL ERROR DETECTED IN APP '{app_label.upper()}'

One or more models in this app have multiple auto-generated fields, which Django doesn't allow.

💡 TO FIX THIS ISSUE:

The error occurs when a model has both:
1. The default 'id' field (auto-generated by Django)
2. Another auto-generated field (like UUIDField with default=uuid.uuid4)

SOLUTION OPTIONS:

Option 1 - Remove auto-generation from one field:
   Change: uuid_field = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
   To:     uuid_field = models.UUIDField(default=uuid.uuid4, unique=True)
   (Remove editable=False)

Option 2 - Use custom primary key:
   class YourModel(models.Model):
       id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
       # Remove the default 'id' field by setting primary_key=True

Option 3 - Remove one of the auto-generated fields entirely

⚠️  After fixing the model, run 'python manage.py makemigrations' and 'python manage.py migrate'

The sync will skip this app until the model errors are fixed.
"""
                    logger.error(suggestion)
                    print(suggestion)  # Also print to console for immediate visibility
                else:
                    logger.error(f"Unknown error loading models from app '{app_label}': {error_message}")
                
                # Continue with other apps instead of crashing
                continue
        
        return models_list
    
    def get_table_name(self, model):
        """Get the actual table name for a model"""
        return model._meta.db_table
    
    def get_default_table_name(self, model):
        """Get the default Django table name"""
        return f"{model._meta.app_label}_{model._meta.model_name}"
    
    def find_existing_table_for_model(self, model):
        """Find existing table that matches the model with case-insensitive comparison
        
        Returns:
            tuple: (existing_table_name, target_table_name) where:
                - existing_table_name: The actual table name in the database (or None if not found)
                - target_table_name: The desired table name (from model's db_table)
        """
        expected_table = self.get_table_name(model)
        default_table = self.get_default_table_name(model)
        model_name = model._meta.model_name
        app_label = model._meta.app_label
        existing_tables = self.inspector.get_existing_tables()
        
        logger.debug(f"Looking for table for model {model.__name__}: expected='{expected_table}', default='{default_table}'")
        logger.debug(f"Available tables: {existing_tables}")
        
        # Create a case-insensitive mapping of existing tables
        table_lower_map = {table.lower(): table for table in existing_tables}
        
        # Check if expected table exists (case-insensitive)
        expected_lower = expected_table.lower()
        if expected_lower in table_lower_map:
            actual_name = table_lower_map[expected_lower]
            logger.debug(f"Found expected table (case-insensitive): '{actual_name}' (expected: '{expected_table}')")
            # If case doesn't match, return the actual name to rename from
            if actual_name != expected_table:
                # Check if the target name already exists (to avoid rename conflicts)
                if expected_table in existing_tables:
                    logger.warning(f"Target table '{expected_table}' already exists, cannot rename '{actual_name}' to '{expected_table}'")
                    # Return the existing table as-is, no rename needed
                    return actual_name, expected_table
                
                # For MySQL, check if this is a case-only change that can be handled by two-step rename
                engine = self.inspector.get_database_engine()
                if engine == 'mysql' and actual_name.lower() == expected_table.lower() and actual_name != expected_table:
                    # This is a case-only change that can be handled by the two-step rename in _rename_table
                    logger.info(f"MySQL case-only change detected: '{actual_name}' -> '{expected_table}' (will use two-step rename)")
                    return actual_name, expected_table
                
                logger.info(f"Table case mismatch detected: '{actual_name}' -> '{expected_table}'")
                return actual_name, expected_table
            logger.debug(f"Table case matches: '{actual_name}'")
            return expected_table, None
        
        # Check if default table exists (case-insensitive)
        default_lower = default_table.lower()
        if default_lower in table_lower_map and default_lower != expected_lower:
            actual_name = table_lower_map[default_lower]
            logger.debug(f"Found default table (case-insensitive): '{actual_name}' (default: '{default_table}')")
            # If default table exists with different case, use that as source for rename
            if actual_name != expected_table:
                # Check if the target name already exists (to avoid rename conflicts)
                if expected_table in existing_tables:
                    logger.warning(f"Target table '{expected_table}' already exists, cannot rename '{actual_name}' to '{expected_table}'")
                    # Return the existing table as-is, no rename needed
                    return expected_table, None
                
                # For MySQL, check if this is a case-only change that can be handled by two-step rename
                engine = self.inspector.get_database_engine()
                if engine == 'mysql' and actual_name.lower() == expected_table.lower() and actual_name != expected_table:
                    # This is a case-only change that can be handled by the two-step rename in _rename_table
                    logger.info(f"MySQL case-only change detected (default table): '{actual_name}' -> '{expected_table}' (will use two-step rename)")
                    return actual_name, expected_table
                
                logger.info(f"Default table case mismatch: '{actual_name}' -> '{expected_table}'")
                return actual_name, expected_table
        
        # Check for any table that might be related to this model (for renamed tables)
        # Look for tables that match the model name or app_model pattern
        possible_old_names = [
            model_name.lower(),
            f"{app_label}_{model_name}".lower(),
            f"{app_label}_{model_name}".replace('_', '').lower(),
            model_name.lower() + 's',  # common pluralization
            model_name.lower() + 'es',  # common pluralization
        ]
        
        logger.debug(f"Checking possible old names: {possible_old_names}")
        
        # Look for any existing table that matches possible old names
        for table in existing_tables:
            table_lower = table.lower()
            if table_lower in possible_old_names and table_lower != expected_lower:
                logger.debug(f"Found possible old table name for {expected_table}: {table}")
                # Check if the target name already exists (to avoid rename conflicts)
                if expected_table in existing_tables:
                    logger.warning(f"Target table '{expected_table}' already exists, cannot rename '{table}' to '{expected_table}'")
                    # Return the existing table as-is, no rename needed
                    return expected_table, None
                
                # For MySQL, check if this is a case-only change that can be handled by two-step rename
                engine = self.inspector.get_database_engine()
                if engine == 'mysql' and table.lower() == expected_table.lower() and table != expected_table:
                    # This is a case-only change that can be handled by the two-step rename in _rename_table
                    logger.info(f"MySQL case-only change detected (possible old name): '{table}' -> '{expected_table}' (will use two-step rename)")
                    return table, expected_table
                
                return table, expected_table
        
        logger.debug(f"No existing table found for model {model.__name__}")
        return None, expected_table
    
    def get_model_columns(self, model):
        """Get column definitions for a Django model"""
        columns = {}
        for field in model._meta.get_fields():
            if hasattr(field, 'column'):
                col_name = field.column
                if hasattr(field, 'db_column') and field.db_column:
                    col_name = field.db_column
                
                try:
                    definition = self.field_mapper.field_to_column_definition(field)
                    if definition is not None:  # Skip ManyToManyField (returns None)
                        columns[col_name] = {
                            'field': field,
                            'definition': definition
                        }
                    else:
                        # This is a ManyToManyField, handle it separately
                        logger.info(f"Skipping ManyToManyField {field} for model {model.__name__} - will handle via intermediate table")
                except Exception as e:
                    logger.warning(f"Could not map field {field} for model {model.__name__}: {e}")
        
        return columns
    
    def sync_single_model(self, model):
        """Synchronize a single model with database"""
        model_name = f"{model._meta.app_label}.{model.__name__}"
        table_name = self.get_table_name(model)
        
        logger.debug(f"Processing model: {model_name} (table: {table_name})")
        
        # Check if this table should be excluded
        if self.field_mapper.should_exclude_table(table_name):
            logger.debug(f"Skipping excluded table: {table_name}")
            logger.info(f"Skipping excluded table: {table_name}")
            return {
                'status': 'skipped',
                'actions': [f"Skipped excluded table: {table_name}"],
                'warnings': [],
                'errors': []
            }
            
        logger.info(f"Syncing model: {model_name} (table: {table_name})")
        
        result = {
            'status': 'success',
            'actions': [],
            'warnings': [],
            'errors': []
        }
        
        try:
            target_table_name = self.get_table_name(model)
            existing_table, rename_target = self.find_existing_table_for_model(model)
            
            # Log the table detection results for debugging
            logger.debug(f"Table detection for {model_name}: existing='{existing_table}', target='{target_table_name}', rename_target='{rename_target}'")
            
            # Handle table creation or renaming
            table_was_created = False
            if not existing_table:
                # Create new table
                if self._create_table(model, target_table_name):
                    result['actions'].append(f"Created table '{target_table_name}'")
                    table_was_created = True
                    existing_table = target_table_name  # Set for further processing
            
            # Handle table renaming
            if rename_target and existing_table and existing_table != rename_target:
                logger.info(f"Found table case mismatch: '{existing_table}' -> '{rename_target}'")
                should_rename = self._should_rename_table(existing_table, rename_target)
                if should_rename:
                    if self._rename_table(existing_table, rename_target):
                        result['actions'].append(f"Renamed table '{existing_table}' to '{rename_target}'")
                        existing_table = rename_target
                    else:
                        result['errors'].append(f"Failed to rename table '{existing_table}'")
                        result['status'] = 'error'
                        return result
                else:
                    result['warnings'].append(f"Table rename skipped: '{existing_table}' -> '{rename_target}'")
                    target_table_name = existing_table
            elif rename_target and not existing_table:
                # This shouldn't happen, but handle it gracefully
                logger.warning(f"Rename target specified but no existing table found: {rename_target}")
                result['warnings'].append(f"Rename target '{rename_target}' specified but no existing table found")
            
            # Sync columns (always run this to handle foreign key constraints)
            working_table = existing_table if existing_table else target_table_name
            column_results = self._sync_columns(model, working_table)
            result['actions'].extend(column_results['actions'])
            result['warnings'].extend(column_results['warnings'])
            result['errors'].extend(column_results['errors'])
        
            # Sync ManyToMany intermediate tables (always run this)
            m2m_results = self._sync_m2m_tables(model)
            result['actions'].extend(m2m_results['actions'])
            result['warnings'].extend(m2m_results['warnings'])
            result['errors'].extend(m2m_results['errors'])
            
            if column_results['errors'] or m2m_results['errors']:
                result['status'] = 'error'
            elif column_results['warnings'] or m2m_results['warnings']:
                result['status'] = 'warning'
        
        except Exception as e:
            error_message = str(e)
            logger.error(f"Error syncing model {model_name}: {error_message}")
            
            # Handle specific Django model errors with helpful suggestions
            if "can't have more than one auto-generated field" in error_message:
                suggestion = f"""
🔧 DJANGO MODEL ERROR DETECTED

Model '{model_name}' has multiple auto-generated fields, which Django doesn't allow.

💡 TO FIX THIS ISSUE:

The error occurs when a model has both:
1. The default 'id' field (auto-generated by Django)
2. Another auto-generated field (like UUIDField with default=uuid.uuid4)

SOLUTION OPTIONS:

Option 1 - Remove auto-generation from one field:
   Change: uuid_field = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
   To:     uuid_field = models.UUIDField(default=uuid.uuid4, unique=True)
   (Remove editable=False)

Option 2 - Use custom primary key:
   class {model.__name__}(models.Model):
       id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
       # Remove the default 'id' field by setting primary_key=True

Option 3 - Remove one of the auto-generated fields entirely

⚠️  After fixing the model, run 'python manage.py makemigrations' and 'python manage.py migrate'
"""
                logger.error(suggestion)
                print(suggestion)  # Also print to console for immediate visibility
                result['errors'].append(f"Model error: {error_message}")
                result['errors'].append("See suggestions above for fixing the Django model")
            elif "Unsupported field type" in error_message:
                suggestion = f"""
🔧 UNSUPPORTED FIELD TYPE DETECTED

Model '{model_name}' contains field types that are not supported by the current database engine.

💡 TO FIX THIS ISSUE:

The sync tool now supports these additional field types:
- DurationField (stored as BIGINT)
- GenericIPAddressField (stored as VARCHAR(45))
- BinaryField (stored as LONGBLOB)
- JSONField (with proper default handling)

If you're still seeing this error, please check:
1. Field type compatibility with your database engine
2. Field configuration (defaults, constraints, etc.)

⚠️  Try running the sync again with the updated field mapper
"""
                logger.error(suggestion)
                print(suggestion)  # Also print to console for immediate visibility
                result['errors'].append(f"Field mapping error: {error_message}")
                result['errors'].append("See suggestions above for fixing the field types")
            elif "You have an error in your SQL syntax" in error_message and "dict" in error_message:
                suggestion = f"""
🔧 JSON FIELD SYNTAX ERROR DETECTED

Model '{model_name}' has a JSONField with an invalid default value configuration.

💡 TO FIX THIS ISSUE:

The error occurs when JSONField has a callable default like `default=dict`.

SOLUTION OPTIONS:

Option 1 - Use a literal default:
   Change: json_field = models.JSONField(default=dict)
   To:     json_field = models.JSONField(default=dict, null=True, blank=True)

Option 2 - Use a function that returns the default:
   Change: json_field = models.JSONField(default=dict)
   To:     json_field = models.JSONField(default=lambda: {{}})

Option 3 - Remove the default entirely:
   Change: json_field = models.JSONField(default=dict)
   To:     json_field = models.JSONField(null=True, blank=True)

⚠️  After fixing the model, run 'python manage.py makemigrations' and 'python manage.py migrate'
"""
                logger.error(suggestion)
                print(suggestion)  # Also print to console for immediate visibility
                result['errors'].append(f"JSON field error: {error_message}")
                result['errors'].append("See suggestions above for fixing the JSON field")
            else:
                result['errors'].append(error_message)
            
            result['status'] = 'error'
        
        return result
    
    def _create_table(self, model, table_name):
        """Create a new table based on Django model"""
        if self.dry_run:
            logger.info(f"[DRY RUN] Would create table: {table_name}")
            return True
        
        try:
            model_columns = self.get_model_columns(model)
            column_definitions = []
            
            for col_name, col_info in model_columns.items():
                column_definitions.append(f"`{col_name}` {col_info['definition']}")
            
            # Get database-specific CREATE TABLE syntax
            engine = self.inspector.get_database_engine()
            if engine == 'mysql':
                create_query = f"""
                CREATE TABLE `{table_name}` (
                    {', '.join(column_definitions)}
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """
            elif engine == 'postgresql':
                create_query = f"""
                CREATE TABLE "{table_name}" (
                    {', '.join(column_definitions)}
                )
                """
            elif engine == 'sqlite':
                create_query = f"""
                CREATE TABLE "{table_name}" (
                    {', '.join(column_definitions)}
                )
                """
            else:
                raise SyncOperationError(f"Unsupported database engine: {engine}")
            
            with transaction.atomic(using=self.database_alias):
                self.inspector.cursor.execute(create_query)
            logger.info(f"Created table: {table_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating table {table_name}: {e}")
            return False
    
    def _should_rename_table(self, old_name, new_name):
        """Check if table should be renamed"""
        if self.auto_approve:
            return True
        
        # Check if this is a case-only change and auto-fix is enabled
        if old_name.lower() == new_name.lower() and old_name != new_name:
            auto_fix_case = get_setting('AUTO_FIX_TABLE_CASE', True)
            if auto_fix_case:
                logger.info(f"Auto-fixing table case: '{old_name}' -> '{new_name}'")
                return True
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Would ask to rename '{old_name}' to '{new_name}'")
            
            # Generate manual SQL command
            engine = self.inspector.get_database_engine()
            if engine == 'mysql':
                manual_cmd = f"RENAME TABLE `{old_name}` TO `{new_name}`;"
            elif engine == 'postgresql':
                manual_cmd = f'ALTER TABLE "{old_name}" RENAME TO "{new_name}";'
            elif engine == 'sqlite':
                manual_cmd = f'ALTER TABLE "{old_name}" RENAME TO "{new_name}";'
            else:
                manual_cmd = f"-- Manual rename command for {engine}: {old_name} -> {new_name}"
            
            self.manual_commands.append({
                'old_name': old_name,
                'new_name': new_name,
                'command': manual_cmd,
                'reason': 'Table name case mismatch'
            })
            
            return True
        
        response = input(f"Rename table '{old_name}' to '{new_name}'? (y/N): ")
        return response.lower() == 'y'
    
    def _rename_table(self, old_name, new_name):
        """Rename a table"""
        if self.dry_run:
            logger.info(f"[DRY RUN] Would rename table: {old_name} -> {new_name}")
            return True
        
        try:
            # Safety check: verify that the target table doesn't already exist
            existing_tables = self.inspector.get_existing_tables()
            logger.debug(f"Renaming '{old_name}' to '{new_name}'")
            logger.debug(f"Existing tables: {existing_tables}")

            # Check for exact match first
            if new_name in existing_tables:
                logger.error(f"Cannot rename '{old_name}' to '{new_name}': target table already exists")
                return False

            # Check for case-insensitive match (for MySQL compatibility)
            engine = self.inspector.get_database_engine()
            if engine == 'mysql':
                table_lower_map = {table.lower(): table for table in existing_tables}
                if new_name.lower() in table_lower_map:
                    existing_table = table_lower_map[new_name.lower()]
                    if existing_table != new_name:
                        # Check if this is a case-only change that we can handle
                        if old_name.lower() == new_name.lower() and old_name != new_name:
                            # This is a case-only change, perform two-step rename
                            temp_name = f"{old_name}_temp_rename"
                            # Ensure temp_name does not exist
                            temp_name_orig = temp_name
                            i = 1
                            while temp_name in existing_tables:
                                temp_name = f"{temp_name_orig}{i}"
                                i += 1
                            try:
                                logger.info(f"Performing two-step rename: '{old_name}' -> '{temp_name}' -> '{new_name}'")
                                with transaction.atomic(using=self.database_alias):
                                    self.inspector.cursor.execute(f"RENAME TABLE `{old_name}` TO `{temp_name}`")
                                    self.inspector.cursor.execute(f"RENAME TABLE `{temp_name}` TO `{new_name}`")
                                logger.info(f"Renamed table: {old_name} -> {new_name} (via {temp_name})")
                                
                                # Check if the rename actually took effect (for case-insensitive MySQL)
                                updated_tables = self.inspector.get_existing_tables()
                                if new_name in updated_tables:
                                    logger.info(f"Table rename confirmed: '{new_name}' now exists in database")
                                    return True
                                elif old_name in updated_tables:
                                    # The rename didn't take effect, likely due to case-insensitive MySQL
                                    logger.warning(f"Table rename may not have taken effect due to MySQL case-insensitive configuration. Table still appears as '{old_name}'")
                                    logger.info(f"Note: This is normal for MySQL servers with case-insensitive table names. The sync will continue with the existing table name.")
                                    
                                    # Provide helpful suggestion for fixing the issue
                                    suggestion = f"""
🔧 MYSQL CASE SENSITIVITY ISSUE DETECTED

The table rename '{old_name}' → '{new_name}' didn't take effect because your MySQL server 
has case-insensitive table names enabled.

💡 TO FIX THIS ISSUE, you can change your MySQL configuration:

Option 1 - Temporary fix (requires SUPER privilege):
   SET GLOBAL lower_case_table_names = 0;

Option 2 - Permanent fix (requires server restart):
   1. Stop MySQL server
   2. Edit MySQL config file (my.cnf or my.ini)
   3. Add: [mysqld]
      lower_case_table_names = 0
   4. Restart MySQL server

⚠️  WARNING: Changing this setting may affect existing tables and applications.
   Make sure to backup your database before making changes.

The sync will continue with the existing table name for now.
"""
                                    logger.info(suggestion)
                                    print(suggestion)  # Also print to console for immediate visibility
                                    return True
                                else:
                                    # Something unexpected happened
                                    logger.error(f"Table rename failed: neither '{old_name}' nor '{new_name}' found in database")
                                    return False
                            except Exception as e:
                                logger.error(f"Error in two-step rename {old_name} -> {temp_name} -> {new_name}: {e}")
                                return False
                        else:
                            # This is not a case-only change, so we have a real conflict
                            logger.error(f"Cannot rename '{old_name}' to '{new_name}': table '{existing_table}' already exists (case-insensitive)")
                            return False
                    else:
                        logger.warning(f"Target table '{new_name}' already exists with exact case match")
                        return False

            engine = self.inspector.get_database_engine()
            if engine == 'mysql':
                rename_query = f"RENAME TABLE `{old_name}` TO `{new_name}`"
            elif engine == 'postgresql':
                rename_query = f'ALTER TABLE "{old_name}" RENAME TO "{new_name}"'
            elif engine == 'sqlite':
                rename_query = f'ALTER TABLE "{old_name}" RENAME TO "{new_name}"'
            else:
                raise SyncOperationError(f"Unsupported database engine: {engine}")

            with transaction.atomic(using=self.database_alias):
                self.inspector.cursor.execute(rename_query)
            logger.info(f"Renamed table: {old_name} -> {new_name}")
            return True

        except Exception as e:
            logger.error(f"Error renaming table {old_name} to {new_name}: {e}")
            return False
    
    def _sync_columns(self, model, table_name):
        """Synchronize columns for a table"""
        result = {
            'actions': [],
            'warnings': [],
            'errors': []
        }
        
        try:
            # Get existing and expected columns
            existing_columns = self._get_existing_columns(table_name)
            model_columns = self.get_model_columns(model)
            
            # Add missing columns
            for col_name, col_info in model_columns.items():
                if col_name not in existing_columns:
                    if self._add_column(table_name, col_name, col_info['definition']):
                        result['actions'].append(f"Added column '{col_name}' to '{table_name}'")
                        
                        # Add foreign key constraint if this is a foreign key field
                        field = col_info['field']
                        if type(field).__name__ in ['ForeignKey', 'OneToOneField']:
                            if self._add_foreign_key_constraint(table_name, col_name, field):
                                result['actions'].append(f"Added foreign key constraint for '{col_name}' in '{table_name}'")
                            else:
                                result['warnings'].append(f"Failed to add foreign key constraint for '{col_name}' in '{table_name}'")
                    else:
                        result['errors'].append(f"Failed to add column '{col_name}' to '{table_name}'")
            
            # Handle extra columns
            for col_name in existing_columns:
                if col_name not in model_columns:
                    if self._should_drop_column(table_name, col_name):
                        if self._drop_column(table_name, col_name):
                            result['actions'].append(f"Dropped column '{col_name}' from '{table_name}'")
                        else:
                            result['errors'].append(f"Failed to drop column '{col_name}' from '{table_name}'")
                    else:
                        result['warnings'].append(f"Extra column '{col_name}' in '{table_name}' (kept)")
            
            # Fix existing foreign key columns that may have wrong defaults or missing constraints
            for col_name, col_info in model_columns.items():
                if col_name in existing_columns:
                    field = col_info['field']
                    field_type = type(field).__name__
                    logger.debug(f"Checking column '{col_name}' in '{table_name}' - field type: {field_type}")
                    
                    if field_type in ['ForeignKey', 'OneToOneField']:
                        logger.debug(f"Found foreign key field '{col_name}' in '{table_name}' - checking if fix needed")
                        # Only check and fix if constraint is actually missing
                        has_constraint = self._check_foreign_key_constraint_exists(table_name, col_name, field)
                        logger.debug(f"Foreign key constraint exists for '{col_name}' in '{table_name}': {has_constraint}")
                        
                        if not has_constraint:
                            logger.info(f"Foreign key constraint missing for '{col_name}' in '{table_name}' - attempting to fix")
                            if self._fix_existing_foreign_key_column(table_name, col_name, field):
                                result['actions'].append(f"Fixed foreign key column '{col_name}' in '{table_name}'")
                            else:
                                result['warnings'].append(f"Could not fully fix foreign key column '{col_name}' in '{table_name}'")
                        else:
                            logger.debug(f"Foreign key constraint already exists for '{col_name}' in '{table_name}' - no fix needed")
            
            # Detect and alter column data types, nullability, and defaults robustly for MySQL and PostgreSQL

            for col_name, col_info in model_columns.items():
                if col_name in existing_columns:
                    field = col_info['field']
                    engine = self.inspector.get_database_engine()
                    db_col = existing_columns[col_name]
                    db_null = getattr(db_col, 'null_ok', None)
                    model_null = getattr(field, 'null', None)
                    model_unique = getattr(field, 'unique', False)
                    model_default = getattr(field, 'default', None)
                    

                    db_default = None
                    db_unique = False
                    is_primary_key = getattr(field, 'primary_key', False)
                    field_type = type(field).__name__
                    # Check if this is a OneToOneField (which is unique by definition)
                    is_one_to_one = field_type == 'OneToOneField'
                    try:
                        if engine == 'mysql':
                            # Get comprehensive column info including PRIMARY KEY status
                            self.inspector.cursor.execute("""
                                SELECT COLUMN_DEFAULT, COLUMN_KEY, EXTRA, IS_NULLABLE, COLUMN_TYPE
                                FROM INFORMATION_SCHEMA.COLUMNS
                                WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s AND COLUMN_NAME = %s
                            """, (table_name, col_name))
                            row = self.inspector.cursor.fetchone()
                            if row:
                                db_default = row[0]
                                db_key = row[1]  # PRI, UNI, MUL, or empty
                                db_extra = row[2]
                                db_is_nullable = row[3]
                                db_column_type = row[4]
                                # Determine if this is a primary key in the DB
                                if db_key == 'PRI' or (db_extra and 'auto_increment' in db_extra.lower()):
                                    is_primary_key = True
                                # Determine if this column is unique in the DB
                                db_unique = db_key in ['PRI', 'UNI']
                        elif engine == 'postgresql':
                            self.inspector.cursor.execute("""
                                SELECT column_default, is_nullable, data_type
                                FROM information_schema.columns
                                WHERE table_name = %s AND column_name = %s
                            """, (table_name, col_name))
                            row = self.inspector.cursor.fetchone()
                            if row:
                                db_default = row[0]
                                db_null = (row[1] == 'YES')
                                db_column_type = row[2]
                            self.inspector.cursor.execute("""
                                SELECT COUNT(*) FROM pg_constraint c
                                JOIN pg_attribute a ON a.attrelid = c.conrelid AND a.attnum = ANY(c.conkey)
                                WHERE c.conrelid = %s::regclass AND a.attname = %s AND c.contype = 'u'
                            """, (table_name, col_name))
                            db_unique = self.inspector.cursor.fetchone()[0] > 0
                    except Exception as e:
                        logger.warning(f"Could not fetch DB default/unique/null for {table_name}.{col_name}: {e}")
                    
                    # Skip processing if this is already a primary key and no changes needed
                    if is_primary_key and col_name == 'id':
                        logger.debug(f"Skipping primary key column '{col_name}' in '{table_name}' - no changes needed")
                        continue
                    
                    # Normalize defaults for booleans
                    db_default_norm = str(db_default).strip().lower() if db_default is not None else None
                    model_default_norm = str(model_default).strip().lower() if model_default is not None else None
                    if engine == 'mysql' and col_info['definition'].split()[0].upper() == 'BOOLEAN':
                        if db_default_norm in ['0', 'false'] and model_default_norm in ['0', 'false', 'no', 'off']:
                            db_default_norm = model_default_norm = '0'
                        elif db_default_norm in ['1', 'true'] and model_default_norm in ['1', 'true', 'yes', 'on']:
                            db_default_norm = model_default_norm = '1'
                    
                    # Build full column definition for MySQL, avoiding duplicate NULL/NOT NULL/DEFAULT
                    if engine == 'mysql':
                        # Start with base type
                        base_def = col_info['definition']
                        # Remove any NULL/NOT NULL/DEFAULT/UNIQUE from base_def
                        base_def = re.sub(r'\b(NULL|NOT NULL|UNIQUE)\b', '', base_def, flags=re.IGNORECASE)
                        base_def = re.sub(r'\bDEFAULT\s+[^ ]+', '', base_def, flags=re.IGNORECASE)
                        base_def = re.sub(r'\s+', ' ', base_def).strip()
                        
                        # For primary key columns, don't add anything extra
                        if is_primary_key:
                            # Primary keys are already UNIQUE NOT NULL AUTO_INCREMENT
                            if 'AUTO_INCREMENT' not in base_def.upper():
                                base_def += ' AUTO_INCREMENT'
                            base_def += ' PRIMARY KEY'
                        else:
                            # Add NULL/NOT NULL for non-primary keys
                            if not model_null:
                                base_def += ' NOT NULL'
                            
                            # Add UNIQUE only if the model field is unique or OneToOneField
                            if model_unique or is_one_to_one:
                                base_def += ' UNIQUE'
                            
                            # Add default value - only add if explicitly set in database
                            if db_default is not None:
                                base_def += f" DEFAULT {db_default}"
                            # Do NOT add DEFAULT NULL for nullable columns unless explicitly present
                        
                        # Get current DB column definition using SHOW CREATE TABLE for accuracy
                        try:
                            self.inspector.cursor.execute(f"SHOW CREATE TABLE `{table_name}`")
                            create_table_result = self.inspector.cursor.fetchone()
                            if create_table_result:
                                create_table_sql = create_table_result[1]
                                # Extract the column definition from CREATE TABLE
                                # Use line-by-line parsing for better reliability
                                lines = create_table_sql.split('\n')
                                db_col_def = ''
                                for line in lines:
                                    # Look for the exact column name with backticks, but not at the start of the line
                                    # This avoids matching table names like "CREATE TABLE `industry` ("
                                    if f'`{col_name}`' in line and not line.strip().startswith('CREATE TABLE'):
                                        # Extract everything after the column name
                                        parts = line.split(f'`{col_name}`')
                                        if len(parts) > 1:
                                            db_col_def = parts[1].strip()
                                            # Remove leading whitespace and trailing comma
                                            db_col_def = re.sub(r'^\s+', '', db_col_def)
                                            db_col_def = re.sub(r',$', '', db_col_def)
                                            break
                                else:
                                    # If not found with backticks, try without backticks
                                    for line in lines:
                                        if f'{col_name}' in line and '`' not in line and not line.strip().startswith('CREATE TABLE'):
                                            # Extract everything after the column name
                                            parts = line.split(f'{col_name}')
                                            if len(parts) > 1:
                                                db_col_def = parts[1].strip()
                                                # Remove leading whitespace and trailing comma
                                                db_col_def = re.sub(r'^\s+', '', db_col_def)
                                                db_col_def = re.sub(r',$', '', db_col_def)
                                                break
                                
                            else:
                                db_col_def = ''
                        except Exception as e:
                            logger.warning(f"Could not get CREATE TABLE for {table_name}: {e}")
                            db_col_def = ''
                        
                        # Use semantic comparison instead of string normalization
                        model_type = col_info['definition'].split()[0].upper()
                        
                        # Clean up DB column definition to remove collation info for comparison
                        db_col_def_clean = db_col_def
                        # Remove COLLATE and CHARACTER SET clauses
                        db_col_def_clean = re.sub(r'\s+COLLATE\s+\w+', '', db_col_def_clean, flags=re.IGNORECASE)
                        db_col_def_clean = re.sub(r'\s+CHARACTER SET\s+\w+', '', db_col_def_clean, flags=re.IGNORECASE)
                        # Remove any remaining utf8mb4_unicode_ci or similar
                        db_col_def_clean = re.sub(r'\s+utf8mb4_unicode_ci', '', db_col_def_clean, flags=re.IGNORECASE)
                        # Remove any trailing commas and whitespace
                        db_col_def_clean = db_col_def_clean.strip().rstrip(',')
                        # Normalize multiple spaces to single space
                        db_col_def_clean = re.sub(r'\s+', ' ', db_col_def_clean)
                        # Lowercase for case-insensitive comparison
                        db_col_def_clean = db_col_def_clean.lower()
                        base_def_clean = base_def.strip().rstrip(',')
                        base_def_clean = re.sub(r'\s+', ' ', base_def_clean).lower()
                        needs_alter = self._semantic_column_differs(db_col_def_clean, base_def_clean, model_type, model_null, model_unique, model_default, col_name, table_name)
                        

                        

                        

                        

                        

                        

                        


                        
                        if needs_alter:
                            alter_query = f'ALTER TABLE `{table_name}` MODIFY COLUMN `{col_name}` {base_def}'
                            if self.dry_run:
                                logger.info(f"[DRY RUN] Would alter column '{col_name}' in '{table_name}' to: {base_def}")
                                result['actions'].append(f"Would alter column '{col_name}' in '{table_name}' to: {base_def}")
                            else:
                                try:
                                    logger.info(f"Executing SQL: {alter_query}")
                                    print(f"🔧 Executing: {alter_query}")  # Console output for immediate visibility
                                    with transaction.atomic(using=self.database_alias):
                                        self.inspector.cursor.execute(alter_query)
                                    
                                    # Verify the change was actually applied
                                    self.inspector.cursor.execute(f"SHOW CREATE TABLE `{table_name}`")
                                    verify_result = self.inspector.cursor.fetchone()
                                    if verify_result:
                                        verify_sql = verify_result[1]
                                        pattern = rf'`{re.escape(col_name)}`\s+([^,\n]+)'
                                        verify_match = re.search(pattern, verify_sql, re.IGNORECASE)
                                        if verify_match:
                                            actual_def = verify_match.group(1).strip()
                                            actual_def = re.sub(r',$', '', actual_def)
                                            print(f"✅ Verified column definition: {actual_def}")
                                            logger.info(f"Verified column definition for '{col_name}': {actual_def}")
                                        else:
                                            print(f"❌ Could not verify column '{col_name}' definition")
                                            logger.warning(f"Could not verify column '{col_name}' definition after ALTER")
                                    
                                    logger.info(f"Altered column '{col_name}' in '{table_name}' to: {base_def}")
                                    result['actions'].append(f"Altered column '{col_name}' in '{table_name}' to: {base_def}")
                                except Exception as e:
                                    error_msg = str(e)
                                    logger.error(f"Error altering column '{col_name}' in '{table_name}': {error_msg}")
                                    print(f"❌ Error altering column '{col_name}' in '{table_name}': {error_msg}")  # Console output
                                    result['errors'].append(f"Error altering column '{col_name}' in '{table_name}': {error_msg}")
                                    
                                    # Check if it's a permissions issue
                                    if "access denied" in error_msg.lower() or "privilege" in error_msg.lower():
                                        permission_error = f"""
🔧 MYSQL PERMISSIONS ISSUE DETECTED

The ALTER statement failed due to insufficient privileges.

💡 TO FIX THIS ISSUE:

Your MySQL user needs ALTER privileges on the database.

SOLUTION:
1. Connect to MySQL as a privileged user (like root)
2. Grant ALTER privileges:
   GRANT ALTER ON {table_name} TO 'your_user'@'your_host';
   -- or for all tables:
   GRANT ALTER ON your_database.* TO 'your_user'@'your_host';
3. Flush privileges:
   FLUSH PRIVILEGES;

Current user: Check with: SELECT USER(), CURRENT_USER();
Current privileges: Check with: SHOW GRANTS;
"""
                                        print(permission_error)
                                        logger.error(permission_error)
                    elif engine == 'postgresql':
                        # PostgreSQL logic remains the same as before
                        if db_null is not None and model_null is not None and db_null != model_null:
                            null_sql = 'DROP NOT NULL' if model_null else 'SET NOT NULL'
                            alter_query = f'ALTER TABLE "{table_name}" ALTER COLUMN "{col_name}" {null_sql}'
                            if self.dry_run:
                                logger.info(f"[DRY RUN] Would alter nullability of '{col_name}' in '{table_name}' to {model_null}")
                                result['actions'].append(f"Would alter nullability of '{col_name}' in '{table_name}' to {model_null}")
                            else:
                                try:
                                    logger.info(f"Executing SQL: {alter_query}")
                                    with transaction.atomic(using=self.database_alias):
                                        self.inspector.cursor.execute(alter_query)
                                    logger.info(f"Altered nullability of '{col_name}' in '{table_name}' to {model_null}")
                                    result['actions'].append(f"Altered nullability of '{col_name}' in '{table_name}' to {model_null}")
                                except Exception as e:
                                    logger.error(f"Error altering nullability of '{col_name}' in '{table_name}': {e}")
                                    result['errors'].append(f"Error altering nullability of '{col_name}' in '{table_name}': {e}")
                        if db_default_norm != model_default_norm:
                            alter_query = f'ALTER TABLE "{table_name}" ALTER COLUMN "{col_name}" SET DEFAULT {repr(model_default)}'
                            if self.dry_run:
                                logger.info(f"[DRY RUN] Would alter default of '{col_name}' in '{table_name}' to {model_default}")
                                result['actions'].append(f"Would alter default of '{col_name}' in '{table_name}' to {model_default}")
                            else:
                                try:
                                    logger.info(f"Executing SQL: {alter_query}")
                                    with transaction.atomic(using=self.database_alias):
                                        self.inspector.cursor.execute(alter_query)
                                    logger.info(f"Altered default of '{col_name}' in '{table_name}' to {model_default}")
                                    result['actions'].append(f"Altered default of '{col_name}' in '{table_name}' to {model_default}")
                                except Exception as e:
                                    logger.error(f"Error altering default for '{col_name}' in '{table_name}': {e}")
                                    result['errors'].append(f"Error altering default for '{col_name}' in '{table_name}': {e}")
                        # Type difference
                        db_type = self._get_exact_column_type(table_name, col_name)
                        model_type = col_info['definition'].split()[0].upper()
                        db_type_base = db_type.split('(')[0].upper() if db_type else ''
                        model_type_base = model_type.split('(')[0].upper() if model_type else ''
                        if db_type_base != model_type_base or db_type.upper() != model_type:
                            alter_query = f'ALTER TABLE "{table_name}" ALTER COLUMN "{col_name}" TYPE {model_type}'
                            if self.dry_run:
                                logger.info(f"[DRY RUN] Would alter type of '{col_name}' in '{table_name}' to {model_type}")
                                result['actions'].append(f"Would alter type of '{col_name}' in '{table_name}' to {model_type}")
                            else:
                                try:
                                    logger.info(f"Executing SQL: {alter_query}")
                                    with transaction.atomic(using=self.database_alias):
                                        self.inspector.cursor.execute(alter_query)
                                    logger.info(f"Altered type of '{col_name}' in '{table_name}' to {model_type}")
                                    result['actions'].append(f"Altered type of '{col_name}' in '{table_name}' to {model_type}")
                                except Exception as e:
                                    logger.error(f"Error altering type for '{col_name}' in '{table_name}': {e}")
                                    result['errors'].append(f"Error altering type for '{col_name}' in '{table_name}': {e}")

            # Improved foreign key check: only report 'Fixed' if FK is actually missing
            for col_name, col_info in model_columns.items():
                if col_name in existing_columns:
                    field = col_info['field']
                    field_type = type(field).__name__
                    if field_type in ['ForeignKey', 'OneToOneField']:
                        # Check for actual FK constraint in DB using the improved method
                        try:
                            has_constraint = self._check_foreign_key_constraint_exists(table_name, col_name, field)
                            # Only fix if FK is missing
                            if not has_constraint:
                                if self._fix_existing_foreign_key_column(table_name, col_name, field):
                                    result['actions'].append(f"Fixed foreign key column '{col_name}' in '{table_name}'")
                                else:
                                    result['warnings'].append(f"Could not fully fix foreign key column '{col_name}' in '{table_name}'")
                        except Exception as e:
                            logger.warning(f"Error checking/fixing FK for {table_name}.{col_name}: {e}")
            
            # TODO: Add column modification logic here
            # Check for columns that exist in both but have different definitions
        
        except Exception as e:
            result['errors'].append(f"Error syncing columns for {table_name}: {e}")
        
        return result
    
    def _get_existing_columns(self, table_name):
        """Get existing columns for a table"""
        try:
            description = self.inspector.get_table_description(table_name)
            return {col.name: col for col in description}
        except Exception as e:
            logger.error(f"Error getting columns for {table_name}: {e}")
            return {}
    
    def _add_column(self, table_name, col_name, col_definition):
        """Add a column to existing table"""
        if self.dry_run:
            logger.info(f"[DRY RUN] Would add column '{col_name}' to '{table_name}'")
            return True
        
        try:
            engine = self.inspector.get_database_engine()
            if engine in ['mysql', 'postgresql']:
                alter_query = f'ALTER TABLE `{table_name}` ADD COLUMN `{col_name}` {col_definition}'
            elif engine == 'sqlite':
                alter_query = f'ALTER TABLE "{table_name}" ADD COLUMN "{col_name}" {col_definition}'
            else:
                raise SyncOperationError(f"Unsupported database engine: {engine}")
            
            with transaction.atomic(using=self.database_alias):
                self.inspector.cursor.execute(alter_query)
            logger.info(f"Added column '{col_name}' to '{table_name}'")
            return True
            
        except Exception as e:
            error_message = str(e).lower()
            
            # Check for NOT NULL constraint errors
            if any(phrase in error_message for phrase in [
                'cannot add a not null column',
                'not null constraint failed',
                'column cannot be null',
                'not null column',
                'default value null'
            ]):
                # Provide user-friendly error message with solutions
                from colorama import Fore, Style
                friendly_error = f"""
                    {Fore.RED}✗ Cannot add NOT NULL column '{col_name}' to existing table '{table_name}'{Style.RESET_ALL}

                    {Fore.YELLOW}📋 SOLUTION OPTIONS:{Style.RESET_ALL}

                    {Fore.CYAN}Option 1:{Style.RESET_ALL} Add a default value to your model field:
                    {Fore.GREEN}{col_name} = models.CharField(max_length=100, default='some_value'){Style.RESET_ALL}

                    {Fore.CYAN}Option 2:{Style.RESET_ALL} Make the field nullable:
                    {Fore.GREEN}{col_name} = models.CharField(max_length=100, null=True, blank=True){Style.RESET_ALL}

                    {Fore.YELLOW}💡 Why this happens:{Style.RESET_ALL} Adding a NOT NULL column to a table with existing data
                    requires a default value for existing rows.
                    """
                logger.error(friendly_error)
                print(friendly_error)  # Also print to console for immediate visibility
            else:
                # Generic error message for other issues
                logger.error(f"Error adding column '{col_name}' to '{table_name}': {e}")
            
            return False
    
    def _should_drop_column(self, table_name, col_name):
        """Check if column should be dropped"""
        if get_setting('AUTO_DROP_COLUMNS', False):
            return True
        
        if self.auto_approve:
            return True
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Would ask to drop column '{col_name}' from '{table_name}'")
            return False
        
        response = input(f"Drop column '{col_name}' from table '{table_name}'? (y/N): ")
        return response.lower() == 'y'
    
    def _drop_column(self, table_name, col_name):
        """Drop a column from table"""
        if self.dry_run:
            logger.info(f"[DRY RUN] Would drop column '{col_name}' from '{table_name}'")
            return True
        
        try:
            engine = self.inspector.get_database_engine()
            if engine == 'sqlite':
                # SQLite doesn't support DROP COLUMN directly
                logger.warning(f"SQLite doesn't support dropping columns: '{col_name}'")
                return False
            
            # First, check and drop any foreign key constraints on this column
            constraints_dropped = self._drop_foreign_key_constraints_for_column(table_name, col_name)
            
            # Now drop the column
            if engine == 'mysql':
                alter_query = f'ALTER TABLE `{table_name}` DROP COLUMN `{col_name}`'
            elif engine == 'postgresql':
                alter_query = f'ALTER TABLE "{table_name}" DROP COLUMN "{col_name}"'
            else:
                raise SyncOperationError(f"Unsupported database engine: {engine}")
            
            with transaction.atomic(using=self.database_alias):
                self.inspector.cursor.execute(alter_query)
            
            if constraints_dropped:
                logger.info(f"Dropped {len(constraints_dropped)} foreign key constraint(s) and column '{col_name}' from '{table_name}'")
            else:
                logger.info(f"Dropped column '{col_name}' from '{table_name}'")
            return True
            
        except Exception as e:
            logger.error(f"Error dropping column '{col_name}' from '{table_name}': {e}")
            return False
    
    def _drop_foreign_key_constraints_for_column(self, table_name, col_name):
        """Drop foreign key constraints that reference a specific column"""
        constraints_dropped = []
        
        try:
            engine = self.inspector.get_database_engine()
            
            if engine == 'mysql':
                # Get foreign key constraints for this table
                self.inspector.cursor.execute(f"""
                    SELECT CONSTRAINT_NAME, COLUMN_NAME
                    FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                    WHERE TABLE_SCHEMA = DATABASE()
                    AND TABLE_NAME = %s
                    AND COLUMN_NAME = %s
                    AND REFERENCED_TABLE_NAME IS NOT NULL
                """, (table_name, col_name))
                
                constraints = self.inspector.cursor.fetchall()
                
                for constraint_name, column_name in constraints:
                    try:
                        drop_fk_query = f'ALTER TABLE `{table_name}` DROP FOREIGN KEY `{constraint_name}`'
                        self.inspector.cursor.execute(drop_fk_query)
                        constraints_dropped.append(constraint_name)
                        logger.info(f"Dropped foreign key constraint '{constraint_name}' from '{table_name}'")
                    except Exception as e:
                        logger.warning(f"Could not drop foreign key constraint '{constraint_name}': {e}")
            
            elif engine == 'postgresql':
                # Get foreign key constraints for this table
                self.inspector.cursor.execute("""
                    SELECT conname, conrelid::regclass AS table_name
                    FROM pg_constraint
                    WHERE contype = 'f'
                    AND conrelid = %s::regclass
                    AND %s = ANY(SELECT attname FROM pg_attribute 
                                WHERE attrelid = conrelid 
                                AND attnum = ANY(conkey))
                """, (table_name, col_name))
                
                constraints = self.inspector.cursor.fetchall()
                
                for constraint_name, _ in constraints:
                    try:
                        drop_fk_query = f'ALTER TABLE "{table_name}" DROP CONSTRAINT "{constraint_name}"'
                        self.inspector.cursor.execute(drop_fk_query)
                        constraints_dropped.append(constraint_name)
                        logger.info(f"Dropped foreign key constraint '{constraint_name}' from '{table_name}'")
                    except Exception as e:
                        logger.warning(f"Could not drop foreign key constraint '{constraint_name}': {e}")
        
        except Exception as e:
            logger.warning(f"Error checking foreign key constraints for {table_name}.{col_name}: {e}")
        
        return constraints_dropped
    
    def _add_foreign_key_constraint(self, table_name, col_name, field):
        """Add a foreign key constraint for a field"""
        logger.info(f"Starting _add_foreign_key_constraint for '{col_name}' in '{table_name}'")
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Would add foreign key constraint for '{col_name}' in '{table_name}'")
            return True
        
        try:
            # Get the referenced table and column
            related_model = field.related_model
            related_table = related_model._meta.db_table
            related_column = related_model._meta.pk.column  # Primary key column
            
            logger.info(f"Related model: {related_model.__name__}, table: {related_table}, column: {related_column}")
            
            # Generate constraint name using the consistent hash method
            constraint_name = f"fk_{table_name}_{col_name}_{self._get_fk_hash(table_name, col_name)}"
            
            engine = self.inspector.get_database_engine()
            
            # Determine ON DELETE behavior
            on_delete_clause = ""
            if hasattr(field, 'on_delete'):
                from django.db import models
                if field.on_delete == models.CASCADE:
                    on_delete_clause = " ON DELETE CASCADE"
                elif field.on_delete == models.SET_NULL:
                    on_delete_clause = " ON DELETE SET NULL"
                elif field.on_delete == models.RESTRICT:
                    on_delete_clause = " ON DELETE RESTRICT"
                elif field.on_delete == models.SET_DEFAULT:
                    on_delete_clause = " ON DELETE SET DEFAULT"
                # PROTECT doesn't have a direct SQL equivalent, treat as RESTRICT
                elif field.on_delete == models.PROTECT:
                    on_delete_clause = " ON DELETE RESTRICT"
            
            if engine == 'mysql':
                fk_query = f"ALTER TABLE `{table_name}` ADD CONSTRAINT `{constraint_name}` FOREIGN KEY (`{col_name}`) REFERENCES `{related_table}` (`{related_column}`){on_delete_clause}"
            
            elif engine == 'postgresql':
                fk_query = f'ALTER TABLE "{table_name}" ADD CONSTRAINT "{constraint_name}" FOREIGN KEY ("{col_name}") REFERENCES "{related_table}" ("{related_column}"){on_delete_clause}'
            
            elif engine == 'sqlite':
                # SQLite doesn't support adding foreign key constraints to existing tables
                logger.warning(f"SQLite doesn't support adding foreign key constraints to existing tables: {col_name}")
                return False
            
            else:
                raise SyncOperationError(f"Unsupported database engine: {engine}")
            
            logger.info(f"Executing FK constraint SQL: {fk_query}")
            
            with transaction.atomic(using=self.database_alias):
                self.inspector.cursor.execute(fk_query)
            
            logger.info(f"Successfully added foreign key constraint '{constraint_name}' for '{col_name}' in '{table_name}'")
            return True
            
        except Exception as e:
            logger.error(f"Error adding foreign key constraint for '{col_name}' in '{table_name}': {e}")
            return False
    
    def _get_fk_hash(self, table_name, col_name):
        """Generate a hash for foreign key constraint names to ensure uniqueness"""
        import hashlib
        hash_input = f"{table_name}_{col_name}"
        return hashlib.md5(hash_input.encode()).hexdigest()[:8]
    
    def _fix_existing_foreign_key_column(self, table_name, col_name, field):
        """Fix existing foreign key column that may have wrong default or missing constraint"""
        logger.info(f"Starting _fix_existing_foreign_key_column for '{col_name}' in '{table_name}'")
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Would fix foreign key column '{col_name}' in '{table_name}'")
            return True
        
        try:
            engine = self.inspector.get_database_engine()
            referenced_table = field.related_model._meta.db_table
            referenced_col = field.target_field.column

            # Find and drop existing FKs for this column
            if engine == 'mysql':
                self.inspector.cursor.execute(
                    """
                    SELECT CONSTRAINT_NAME, REFERENCED_TABLE_NAME
                    FROM information_schema.KEY_COLUMN_USAGE
                    WHERE TABLE_SCHEMA = DATABASE()
                      AND TABLE_NAME = %s
                      AND COLUMN_NAME = %s
                      AND REFERENCED_TABLE_NAME IS NOT NULL
                    """,
                    [table_name, col_name]
                )
                for constraint_name, ref_table in self.inspector.cursor.fetchall():
                    logger.info(f"Dropping FK {constraint_name} (points to {ref_table})")
                    self.inspector.cursor.execute(f"ALTER TABLE `{table_name}` DROP FOREIGN KEY `{constraint_name}`")
            
            elif engine == 'postgresql':
                self.inspector.cursor.execute("""
                    SELECT c.conname
                    FROM pg_constraint c
                    JOIN pg_class t ON t.oid = c.conrelid
                    JOIN pg_attribute a ON a.attrelid = c.conrelid AND a.attnum = ANY(c.conkey)
                    WHERE c.contype = 'f'
                    AND t.relname = %s
                    AND a.attname = %s
                """, (table_name, col_name))
                for constraint_name, in self.inspector.cursor.fetchall():
                    logger.info(f"Dropping FK {constraint_name}")
                    self.inspector.cursor.execute(f'ALTER TABLE "{table_name}" DROP CONSTRAINT "{constraint_name}"')

            # Now add the correct FK using the existing method
            return self._add_foreign_key_constraint(table_name, col_name, field)
            
        except Exception as e:
            logger.error(f"Error fixing foreign key column '{col_name}' in '{table_name}': {e}")
            return False
    
    def _sync_m2m_tables(self, model):
        """Synchronize ManyToMany intermediate tables for a model"""
        result = {
            'actions': [],
            'warnings': [],
            'errors': []
        }
        
        try:
            # Find all ManyToMany fields in the model
            m2m_fields = []
            for field in model._meta.get_fields():
                if type(field).__name__ == 'ManyToManyField':
                    m2m_fields.append(field)
            
            if not m2m_fields:
                return result  # No M2M fields to process
            
            logger.info(f"Found {len(m2m_fields)} ManyToMany field(s) in {model.__name__}")
            
            for field in m2m_fields:
                try:
                    # Get the intermediate table name using Django's internal method
                    through_model = field.remote_field.through
                    if through_model._meta.auto_created:
                        # Auto-created intermediate table
                        intermediate_table = through_model._meta.db_table
                        logger.info(f"Processing M2M intermediate table: {intermediate_table}")
                        
                        # Check if intermediate table exists
                        existing_tables = self.inspector.get_existing_tables()
                        if intermediate_table not in existing_tables:
                            # Create the intermediate table
                            if self._create_m2m_table(field, intermediate_table):
                                result['actions'].append(f"Created ManyToMany table '{intermediate_table}' for field '{field.name}'")
                            else:
                                result['errors'].append(f"Failed to create ManyToMany table '{intermediate_table}' for field '{field.name}'")
                        else:
                            logger.debug(f"ManyToMany table '{intermediate_table}' already exists")
                            # TODO: Add logic to verify/fix intermediate table structure
                    else:
                        # Custom through model - let regular sync handle it
                        logger.info(f"Skipping custom through model for field '{field.name}' - will be handled by regular model sync")
                        
                except Exception as e:
                    result['errors'].append(f"Error processing ManyToMany field '{field.name}': {e}")
                    logger.error(f"Error processing ManyToMany field '{field.name}': {e}")
            
        except Exception as e:
            result['errors'].append(f"Error syncing ManyToMany tables for {model.__name__}: {e}")
            logger.error(f"Error syncing ManyToMany tables for {model.__name__}: {e}")
        
        return result
    
    def _create_m2m_table(self, field, table_name):
        """Create a ManyToMany intermediate table"""
        if self.dry_run:
            logger.info(f"[DRY RUN] Would create ManyToMany table: {table_name}")
            return True
        
        try:
            # Get the source and target models
            source_model = field.model
            target_model = field.related_model
            
            # Get exact primary key column types from database
            source_pk_type = self._get_exact_column_type(source_model._meta.db_table, 'id')
            target_pk_type = self._get_exact_column_type(target_model._meta.db_table, 'id')
            
            # Generate column names (Django convention)
            source_column = f"{source_model._meta.model_name}_id"
            target_column = f"{target_model._meta.model_name}_id"
            
            # Handle self-referencing ManyToMany (same model)
            if source_model == target_model:
                source_column = "from_fullfieldmodel_id"
                target_column = "to_fullfieldmodel_id"
            
            # Create table SQL
            engine = self.inspector.get_database_engine()
            if engine == 'mysql':
                create_query = f"""
                CREATE TABLE `{table_name}` (
                    `id` INT AUTO_INCREMENT PRIMARY KEY,
                    `{source_column}` {source_pk_type} NOT NULL,
                    `{target_column}` {target_pk_type} NOT NULL,
                    UNIQUE KEY `{table_name}_unique` (`{source_column}`, `{target_column}`),
                    KEY `{table_name}_from_idx` (`{source_column}`),
                    KEY `{table_name}_to_idx` (`{target_column}`),
                    CONSTRAINT `{table_name}_from_fk` FOREIGN KEY (`{source_column}`) REFERENCES `{source_model._meta.db_table}` (`id`) ON DELETE CASCADE,
                    CONSTRAINT `{table_name}_to_fk` FOREIGN KEY (`{target_column}`) REFERENCES `{target_model._meta.db_table}` (`id`) ON DELETE CASCADE
                ) ENGINE=InnoDB
                """
            elif engine == 'postgresql':
                create_query = f"""
                CREATE TABLE "{table_name}" (
                    "id" SERIAL PRIMARY KEY,
                    "{source_column}" {source_pk_type} NOT NULL,
                    "{target_column}" {target_pk_type} NOT NULL,
                    CONSTRAINT "{table_name}_{source_column}_{target_column}_unique" UNIQUE ("{source_column}", "{target_column}")
                )
                """
            elif engine == 'sqlite':
                create_query = f"""
                CREATE TABLE "{table_name}" (
                    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
                    "{source_column}" {source_pk_type} NOT NULL,
                    "{target_column}" {target_pk_type} NOT NULL,
                    UNIQUE ("{source_column}", "{target_column}")
                )
                """
            else:
                raise SyncOperationError(f"Unsupported database engine: {engine}")
            
            with transaction.atomic(using=self.database_alias):
                self.inspector.cursor.execute(create_query)
            
            logger.info(f"Created ManyToMany table: {table_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating ManyToMany table {table_name}: {e}")
            return False
    
    def _get_exact_column_type(self, table_name, column_name):
        """Get the exact column type from the database including default value"""
        try:
            engine = self.inspector.get_database_engine()
            
            if engine == 'mysql':
                self.inspector.cursor.execute(f"""
                    SELECT COLUMN_TYPE, COLUMN_DEFAULT, IS_NULLABLE
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_SCHEMA = DATABASE()
                    AND TABLE_NAME = %s
                    AND COLUMN_NAME = %s
                """, (table_name, column_name))
                
                result = self.inspector.cursor.fetchone()
                if result:
                    column_type = result[0].upper()
                    column_default = result[1]
                    is_nullable = result[2] == 'YES'
                    
                    # Build complete column definition
                    definition = column_type
                    
                    # Add nullability - only add NOT NULL explicitly, omit NULL for nullable columns
                    # This matches Django's behavior where nullable columns don't have explicit NULL keyword
                    if not is_nullable:
                        definition += " NOT NULL"
                    
                    # Add default value - only add if explicitly set in database
                    if column_default is not None:
                        if isinstance(column_default, str) and not column_default.isdigit():
                            definition += f" DEFAULT '{column_default}'"
                        else:
                            definition += f" DEFAULT {column_default}"
                    
                    return definition
                    
            elif engine == 'postgresql':
                self.inspector.cursor.execute(f"""
                    SELECT data_type, column_default, is_nullable
                    FROM information_schema.columns
                    WHERE table_name = %s AND column_name = %s
                """, (table_name, column_name))
                
                result = self.inspector.cursor.fetchone()
                if result:
                    data_type = result[0].upper()
                    column_default = result[1]
                    is_nullable = result[2] == 'YES'
                    
                    # Build complete column definition
                    definition = data_type
                    
                    # Add nullability
                    if not is_nullable:
                        definition += " NOT NULL"
                    
                    # Add default value
                    if column_default is not None:
                        definition += f" DEFAULT {column_default}"
                    # Do NOT add DEFAULT NULL for nullable columns unless explicitly present
                    
                    return definition
                    
            elif engine == 'sqlite':
                self.inspector.cursor.execute(f"PRAGMA table_info({table_name})")
                columns = self.inspector.cursor.fetchall()
                for col in columns:
                    if col[1] == column_name:  # col[1] is column name
                        column_type = col[2].upper()  # col[2] is column type
                        not_null = col[3]  # col[3] is not null flag
                        default_value = col[4]  # col[4] is default value
                        
                        definition = column_type
                        if not_null:
                            definition += " NOT NULL"
                        if default_value is not None:
                            definition += f" DEFAULT {default_value}"
                        
                        return definition
            
            # Fallback to default type if not found
            logger.warning(f"Could not determine exact type for {table_name}.{column_name}, using BIGINT")
            return 'BIGINT'
            
        except Exception as e:
            logger.error(f"Error getting column type for {table_name}.{column_name}: {e}")
            return 'BIGINT'  # Safe fallback
    
    def _check_foreign_key_constraint_exists(self, table_name, col_name, field):
        """Check if a foreign key constraint already exists for this column pointing to the correct table"""
        try:
            engine = self.inspector.get_database_engine()
            referenced_table = field.related_model._meta.db_table
            referenced_col = field.target_field.column
            
            if engine == 'mysql':
                self.inspector.cursor.execute(f"""
                    SELECT CONSTRAINT_NAME
                    FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                    WHERE TABLE_SCHEMA = DATABASE()
                    AND TABLE_NAME = %s
                    AND COLUMN_NAME = %s
                    AND REFERENCED_TABLE_NAME = %s
                    AND REFERENCED_COLUMN_NAME = %s
                """, (table_name, col_name, referenced_table, referenced_col))
                
                constraints = self.inspector.cursor.fetchall()
                has_constraint = len(constraints) > 0
                logger.debug(f"MySQL constraint check for {table_name}.{col_name} -> {referenced_table}.{referenced_col}: found {len(constraints)} constraints")
                return has_constraint
            
            elif engine == 'postgresql':
                self.inspector.cursor.execute("""
                    SELECT c.conname
                    FROM pg_constraint c
                    JOIN pg_class t ON t.oid = c.conrelid
                    JOIN pg_class ft ON ft.oid = c.confrelid
                    JOIN pg_attribute a ON a.attrelid = c.conrelid AND a.attnum = ANY(c.conkey)
                    JOIN pg_attribute fa ON fa.attrelid = c.confrelid AND fa.attnum = ANY(c.confkey)
                    WHERE c.contype = 'f'
                    AND t.relname = %s
                    AND a.attname = %s
                    AND ft.relname = %s
                    AND fa.attname = %s
                """, (table_name, col_name, referenced_table, referenced_col))
                
                constraints = self.inspector.cursor.fetchall()
                has_constraint = len(constraints) > 0
                logger.debug(f"PostgreSQL constraint check for {table_name}.{col_name} -> {referenced_table}.{referenced_col}: found {len(constraints)} constraints")
                return has_constraint
            
            return False
            
        except Exception as e:
            logger.warning(f"Error checking foreign key constraint for {table_name}.{col_name}: {e}")
            # If we can't check, assume constraint exists to avoid false positives
            return True
    
    def sync_all_models(self):
        """Synchronize all models with database"""
        models_to_sync = self.get_models_to_sync()
        logger.info(f"Starting sync for {len(models_to_sync)} models")
        
        for model in models_to_sync:
            model_key = f"{model._meta.app_label}.{model.__name__}"
            self.results[model_key] = self.sync_single_model(model)
        
        return self.results
    
    def get_orphaned_tables(self):
        """Find tables in database that don't correspond to any Django model"""
        existing_tables = self.inspector.get_existing_tables()
        models_list = self.get_models_to_sync()
        
        # Get all expected table names from models
        model_tables = set()
        model_tables_lower = set()  # Case-insensitive set for comparison
        for model in models_list:
            expected_table = self.get_table_name(model)
            default_table = self.get_default_table_name(model)
            model_tables.add(expected_table)
            model_tables.add(default_table)
            model_tables_lower.add(expected_table.lower())
            model_tables_lower.add(default_table.lower())
            
            # Add ManyToMany intermediate table names
            for field in model._meta.get_fields():
                if type(field).__name__ == 'ManyToManyField':
                    try:
                        through_model = field.remote_field.through
                        if through_model._meta.auto_created:
                            intermediate_table = through_model._meta.db_table
                            model_tables.add(intermediate_table)
                            model_tables_lower.add(intermediate_table.lower())
                            logger.debug(f"Added M2M intermediate table to expected tables: {intermediate_table}")
                    except Exception as e:
                        logger.warning(f"Error processing M2M field {field.name} for orphaned table detection: {e}")
        
        # Find orphaned tables with details
        orphaned_tables = []
        for table in existing_tables:
            # Check both exact match and case-insensitive match
            if table not in model_tables and table.lower() not in model_tables_lower:
                # Skip Django system tables
                if self.field_mapper.should_exclude_table(table):
                    continue
                
                table_info = self._get_table_info(table)
                orphaned_tables.append({
                    'name': table,
                    'rows': table_info.get('rows', 0),
                    'size_mb': table_info.get('size_mb', 0),
                    'columns': table_info.get('columns', 0)
                })
        
        return orphaned_tables
    
    def _get_table_info(self, table_name):
        """Get basic information about a table"""
        try:
            # Get row count
            self.inspector.cursor.execute(f"SELECT COUNT(*) FROM `{table_name}`")
            row_count = self.inspector.cursor.fetchone()[0]
            
            # Get column count
            description = self.inspector.get_table_description(table_name)
            column_count = len(description)
            
            # Get table size (MySQL specific)
            size_mb = 0
            if self.inspector.get_database_engine() == 'mysql':
                self.inspector.cursor.execute(f"""
                    SELECT ROUND(((data_length + index_length) / 1024 / 1024), 2) AS 'Size_MB'
                    FROM information_schema.tables 
                    WHERE table_schema = DATABASE() AND table_name = %s
                """, (table_name,))
                size_result = self.inspector.cursor.fetchone()
                if size_result and size_result[0]:
                    size_mb = size_result[0]
            
            return {
                'rows': row_count,
                'columns': column_count,
                'size_mb': size_mb
            }
            
        except Exception as e:
            logger.error(f"Error getting info for table {table_name}: {e}")
            return {'rows': 'Unknown', 'columns': 'Unknown', 'size_mb': 'Unknown'}
    
    def drop_orphaned_tables_with_dependencies(self, orphaned_tables):
        """Drop orphaned tables in dependency order (child tables first)"""
        if not orphaned_tables:
            return []
            
        # Get table names from orphaned table objects
        table_names = [table['name'] for table in orphaned_tables]
        
        # Build dependency graph
        dependencies = self._build_table_dependency_graph(table_names)
        
        # Sort tables by dependency order (child tables first)
        sorted_tables = self._topological_sort_tables(table_names, dependencies)
        
        dropped_tables = []
        failed_tables = []
        
        for table_name in sorted_tables:
            if self._drop_single_orphaned_table(table_name):
                dropped_tables.append(table_name)
            else:
                failed_tables.append(table_name)
                
        return {'dropped': dropped_tables, 'failed': failed_tables}
    
    def _build_table_dependency_graph(self, table_names):
        """Build a dependency graph showing which tables reference which other tables"""
        dependencies = {}
        
        for table_name in table_names:
            dependencies[table_name] = set()
            
            try:
                # Get foreign key constraints for this table
                constraints = self.inspector.get_foreign_key_constraints(table_name)
                
                for constraint_name, constraint_info in constraints.items():
                    referenced_table = constraint_info.get('referred_table')
                    if referenced_table and referenced_table in table_names:
                        # This table depends on (references) the referenced_table
                        # So referenced_table must be dropped AFTER this table
                        dependencies[table_name].add(referenced_table)
                        
            except Exception as e:
                logger.warning(f"Could not get FK constraints for {table_name}: {e}")
                
        return dependencies
    
    def _topological_sort_tables(self, table_names, dependencies):
        """Sort tables in dependency order using topological sort (child tables first)"""
        # Kahn's algorithm for topological sorting
        in_degree = {table: 0 for table in table_names}
        
        # Calculate in-degrees (how many tables depend on each table)
        for table in table_names:
            for referenced_table in dependencies[table]:
                in_degree[referenced_table] += 1
        
        # Start with tables that have no incoming dependencies (child tables)
        queue = [table for table in table_names if in_degree[table] == 0]
        sorted_tables = []
        
        while queue:
            current_table = queue.pop(0)
            sorted_tables.append(current_table)
            
            # Remove this table from dependencies and update in-degrees
            for referenced_table in dependencies[current_table]:
                in_degree[referenced_table] -= 1
                if in_degree[referenced_table] == 0:
                    queue.append(referenced_table)
        
        # If we couldn't sort all tables, there might be circular dependencies
        if len(sorted_tables) != len(table_names):
            logger.warning("Possible circular dependencies detected in orphaned tables")
            # Add remaining tables to the end
            remaining = set(table_names) - set(sorted_tables)
            sorted_tables.extend(remaining)
            
        return sorted_tables
    
    def _drop_single_orphaned_table(self, table_name):
        """Drop a single orphaned table from the database"""
        if self.dry_run:
            logger.info(f"[DRY RUN] Would drop orphaned table: {table_name}")
            return True
        
        try:
            engine = self.inspector.get_database_engine()
            if engine == 'mysql':
                drop_query = f"DROP TABLE `{table_name}`"
            elif engine == 'postgresql':
                drop_query = f'DROP TABLE "{table_name}"'
            elif engine == 'sqlite':
                drop_query = f'DROP TABLE "{table_name}"'
            else:
                raise SyncOperationError(f"Unsupported database engine: {engine}")
            
            with transaction.atomic(using=self.database_alias):
                self.inspector.cursor.execute(drop_query)
            logger.info(f"Dropped orphaned table: {table_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error dropping orphaned table {table_name}: {e}")
            return False
    
    def drop_orphaned_table(self, table_name):
        """Drop an orphaned table from the database (legacy method for compatibility)"""
        return self._drop_single_orphaned_table(table_name)
    
    def create_backup(self):
        """Create database backup before sync"""
        import os
        import subprocess
        from datetime import datetime
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f"backup_{self.database_alias}_{timestamp}.sql"
        
        try:
            engine = self.inspector.get_database_engine()
            db_settings = self.inspector.connection.settings_dict
            
            if engine == 'mysql':
                # MySQL backup using mysqldump
                cmd = [
                    'mysqldump',
                    f"--host={db_settings.get('HOST', 'localhost')}",
                    f"--port={db_settings.get('PORT', 3306)}",
                    f"--user={db_settings['USER']}",
                    f"--password={db_settings['PASSWORD']}",
                    '--single-transaction',
                    '--routines',
                    '--triggers',
                    db_settings['NAME']
                ]
                
                with open(backup_file, 'w') as f:
                    result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)
                    
                if result.returncode != 0:
                    logger.error(f"MySQL backup failed: {result.stderr}")
                    return None
                    
            elif engine == 'postgresql':
                # PostgreSQL backup using pg_dump
                env = os.environ.copy()
                env['PGPASSWORD'] = db_settings['PASSWORD']
                
                cmd = [
                    'pg_dump',
                    f"--host={db_settings.get('HOST', 'localhost')}",
                    f"--port={db_settings.get('PORT', 5432)}",
                    f"--username={db_settings['USER']}",
                    '--format=plain',
                    '--no-owner',
                    '--no-privileges',
                    db_settings['NAME']
                ]
                
                with open(backup_file, 'w') as f:
                    result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True, env=env)
                    
                if result.returncode != 0:
                    logger.error(f"PostgreSQL backup failed: {result.stderr}")
                    return None
                    
            elif engine == 'sqlite':
                # SQLite backup using .dump command
                cmd = ['sqlite3', db_settings['NAME'], '.dump']
                
                with open(backup_file, 'w') as f:
                    result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)
                    
                if result.returncode != 0:
                    logger.error(f"SQLite backup failed: {result.stderr}")
                    return None
            else:
                logger.warning(f"Backup not supported for database engine: {engine}")
                return None
                
            # Verify backup file was created and has content
            if os.path.exists(backup_file) and os.path.getsize(backup_file) > 0:
                logger.info(f"Backup created successfully: {backup_file}")
                return backup_file
            else:
                logger.error(f"Backup file was not created or is empty: {backup_file}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return None

    def display_manual_commands(self):
        """Display collected manual SQL commands for table renames"""
        if not self.manual_commands:
            return
        
        print("\n" + "="*60)
        print("🔧 MANUAL SQL COMMANDS FOR TABLE RENAMES")
        print("="*60)
        print("The following SQL commands can be run manually to rename tables:")
        print()
        
        for i, cmd_info in enumerate(self.manual_commands, 1):
            print(f"{i}. {cmd_info['reason']}: '{cmd_info['old_name']}' → '{cmd_info['new_name']}'")
            print(f"   SQL: {cmd_info['command']}")
            print()
        
        print("💡 Instructions:")
        print("   1. Connect to your database using your preferred SQL client")
        print("   2. Run the commands above one by one")
        print("   3. Run 'python manage.py dbsync' again to complete the sync")
        print("   4. Make sure to backup your database before running these commands!")
        print("="*60)

    def _semantic_column_differs(self, db_col_def, model_col_def, model_type, model_null, model_unique, model_default, col_name, table_name):
        """
        Semantic comparison of column definitions to avoid false positives.
        Returns True if the columns actually differ in meaningful ways.
        """
        if not db_col_def:
            return True  # Missing DB column
        
        db_lower = db_col_def.lower()
        model_lower = model_col_def.lower()
        
        # Extract semantic properties from DB column
        db_type = self._extract_db_column_type(db_lower)
        # For nullability, check if 'NOT NULL' is explicitly present
        # If 'NOT NULL' is not present, the column is nullable (MySQL default behavior)
        db_is_null = 'not null' not in db_lower
        db_default = self._extract_db_default(db_col_def)  # Don't lowercase for default extraction to preserve case
        
        # For nullable columns without explicit defaults, treat NULL as equivalent to DEFAULT NULL
        if db_is_null and db_default is None:
            # This is equivalent to having DEFAULT NULL
            db_default = None
        
        # For unique constraints, we need to check the actual database constraints, not just the column definition
        db_is_unique = self._check_column_has_unique_constraint(col_name, table_name)
        
        # Extract semantic properties from model column  
        model_type_norm = self._normalize_model_type(model_type)
        
        # Compare data types (with MySQL-specific mappings)
        type_differs = not self._types_equivalent(db_type, model_type_norm)
        if type_differs:
            return True
            
        # Compare nullability
        null_differs = db_is_null != model_null
        if null_differs:
            return True
            
        # Compare defaults (with special handling for None/NULL and boolean values)
        # For nullable columns, treat missing DEFAULT NULL as equivalent to having DEFAULT NULL
        # This handles the case where MySQL doesn't store DEFAULT NULL explicitly for nullable columns
        if model_null and model_default is None and (db_default is None or db_default == 'NULL'):
            # Both are nullable with no explicit default - equivalent
            pass
        else:
            defaults_differ = not self._defaults_equivalent(db_default, model_default, model_type)
            if defaults_differ:
                return True
            
        # Compare unique constraints (skip for primary keys)
        unique_differs = False
        if not col_name.endswith('_id') and col_name != 'id':  # Skip PK and FK checks
            unique_differs = db_is_unique != model_unique
            if unique_differs:
                return True
        
        return False
    
    def _extract_db_column_type(self, db_def):
        """Extract the full data type from DB column definition including parameters"""
        # Handle common MySQL types with parameters
        if 'tinyint(1)' in db_def:
            return 'boolean'
        elif 'varchar(' in db_def:
            # Extract the full VARCHAR definition including max_length
            import re
            match = re.search(r'varchar\((\d+)\)', db_def, re.IGNORECASE)
            if match:
                max_length = match.group(1)
                return f'varchar({max_length})'
            return 'varchar'
        elif 'bigint' in db_def:
            return 'bigint'
        elif 'int(' in db_def or db_def.startswith('int '):
            return 'int'
        elif 'text' in db_def:
            return 'text'
        elif 'datetime' in db_def:
            return 'datetime'
        elif 'date' in db_def:
            return 'date'
        elif 'decimal(' in db_def:
            # Extract the full DECIMAL definition including precision and scale
            import re
            match = re.search(r'decimal\((\d+),(\d+)\)', db_def, re.IGNORECASE)
            if match:
                precision = match.group(1)
                scale = match.group(2)
                return f'decimal({precision},{scale})'
            return 'decimal'
        elif 'float' in db_def:
            return 'float'
        elif 'time' in db_def:
            return 'time'
        elif 'smallint' in db_def:
            return 'smallint'
        else:
            # For any other type, just return the first word (the type name)
            return db_def.split()[0] if db_def else ''
            
    def _normalize_model_type(self, model_type):
        """Normalize Django model type to match DB comparison"""
        model_lower = model_type.lower()
        if model_lower.startswith('boolean'):
            return 'boolean'
        elif model_lower.startswith('varchar'):
            # Preserve VARCHAR with length parameters
            import re
            match = re.search(r'varchar\((\d+)\)', model_lower)
            if match:
                max_length = match.group(1)
                return f'varchar({max_length})'
            return 'varchar'
        elif model_lower.startswith('bigint'):
            return 'bigint'
        elif model_lower.startswith('int'):
            return 'int'
        elif model_lower.startswith('text'):
            return 'text'
        elif model_lower.startswith('datetime'):
            return 'datetime'
        elif model_lower.startswith('date'):
            return 'date'
        elif model_lower.startswith('decimal'):
            # Preserve DECIMAL with precision and scale
            import re
            match = re.search(r'decimal\((\d+),(\d+)\)', model_lower)
            if match:
                precision = match.group(1)
                scale = match.group(2)
                return f'decimal({precision},{scale})'
            return 'decimal'
        elif model_lower.startswith('float'):
            return 'float'
        elif model_lower.startswith('time'):
            return 'time'
        elif model_lower.startswith('smallint'):
            return 'smallint'
        else:
            return model_lower.split()[0] if model_lower else ''
            
    def _types_equivalent(self, db_type, model_type):
        """Check if database and model types are equivalent including parameters"""
        # Normalize both types to lowercase for comparison
        db_type_lower = db_type.lower()
        model_type_lower = model_type.lower()
        
        # Direct comparison first
        if db_type_lower == model_type_lower:
            return True
        
        # Handle VARCHAR with max_length parameters
        if 'varchar(' in db_type_lower and 'varchar(' in model_type_lower:
            import re
            db_match = re.search(r'varchar\((\d+)\)', db_type_lower)
            model_match = re.search(r'varchar\((\d+)\)', model_type_lower)
            if db_match and model_match:
                db_length = int(db_match.group(1))
                model_length = int(model_match.group(1))
                return db_length == model_length
        
        # Handle DECIMAL with precision and scale
        if 'decimal(' in db_type_lower and 'decimal(' in model_type_lower:
            import re
            db_match = re.search(r'decimal\((\d+),(\d+)\)', db_type_lower)
            model_match = re.search(r'decimal\((\d+),(\d+)\)', model_type_lower)
            if db_match and model_match:
                db_precision = int(db_match.group(1))
                db_scale = int(db_match.group(2))
                model_precision = int(model_match.group(1))
                model_scale = int(model_match.group(2))
                return db_precision == model_precision and db_scale == model_scale
        
        return False
        
    def _extract_db_default(self, db_def):
        """Extract default value from DB column definition"""
        import re
        
        # Handle NULL default
        if re.search(r'default\s+null\b', db_def, re.IGNORECASE):
            return None
        
        # Look for DEFAULT clause
        default_match = re.search(r'default\s+(.+?)(?:\s|$)', db_def, re.IGNORECASE)
        if not default_match:
            return None
            
        default_value = default_match.group(1).strip()
        
        # Handle quoted string defaults (e.g., DEFAULT 'N')
        if default_value.startswith("'") and default_value.endswith("'"):
            return default_value[1:-1]  # Remove quotes
        
        # Handle numeric defaults
        try:
            if '.' in default_value:
                return float(default_value)
            else:
                return int(default_value)
        except ValueError:
            pass
        
        # Handle boolean defaults
        if default_value.lower() in ['true', '1']:
            return True
        elif default_value.lower() in ['false', '0']:
            return False
        
        # Return as string if no other type matches
        return default_value
        
    def _defaults_equivalent(self, db_default, model_default, model_type):
        """Check if database and model defaults are equivalent"""
        from django.db.models.fields import NOT_PROVIDED
        
        # Normalize NOT_PROVIDED to None for comparison
        if model_default is NOT_PROVIDED:
            model_default = None
            
        # Handle None/NULL equivalence
        if db_default is None and model_default is None:
            return True
        if db_default is None and model_default is not None:
            return False
        if db_default is not None and model_default is None:
            return False
            
        # Handle boolean equivalence (True/1, False/0)
        if model_type.upper().startswith('BOOLEAN'):
            # Normalize both to integers for comparison
            model_val = 1 if model_default else 0 if model_default is not None else None
            db_val = int(db_default) if db_default is not None and str(db_default).isdigit() else db_default
            
            if model_val == db_val:
                return True
            # Additional checks for string representations
            if model_default == 1 and str(db_default) in ['1', 'true', 'True']:
                return True
            if model_default == 0 and str(db_default) in ['0', 'false', 'False']:
                return True
                
        # Handle string defaults (e.g., DEFAULT 'N')
        if isinstance(model_default, str) and isinstance(db_default, str):
            # Direct string comparison
            if model_default == db_default:
                return True
            # Also try case-insensitive comparison
            if model_default.lower() == db_default.lower():
                return True
                
        # Handle decimal/float defaults (e.g., 0.0 vs 0.00)
        if model_type.upper().startswith('DECIMAL') or model_type.upper().startswith('FLOAT'):
            try:
                model_float = float(model_default) if model_default is not None else None
                db_float = float(db_default) if db_default is not None else None
                if model_float == db_float:
                    return True
            except (ValueError, TypeError):
                pass
                
        # Final string comparison for other types
        return str(db_default) == str(model_default)
        
    def _check_column_has_unique_constraint(self, col_name, table_name):
        """Check if a column has a unique constraint by querying the database"""
        from django.db import connections
        try:
            with connections[self.database_alias].cursor() as cursor:
                if self.inspector.get_database_engine() == 'mysql':
                    # Query MySQL information_schema for unique constraints
                    cursor.execute("""
                        SELECT COUNT(*) FROM information_schema.statistics 
                        WHERE table_schema = DATABASE() 
                        AND table_name = %s 
                        AND column_name = %s 
                        AND non_unique = 0
                        AND index_name != 'PRIMARY'
                    """, [table_name, col_name])
                    count = cursor.fetchone()[0]
                    return count > 0
                elif self.inspector.get_database_engine() == 'postgresql':
                    # Query PostgreSQL for unique constraints
                    cursor.execute("""
                        SELECT COUNT(*) FROM information_schema.table_constraints tc
                        JOIN information_schema.constraint_column_usage ccu ON tc.constraint_name = ccu.constraint_name
                        WHERE tc.table_name = %s AND ccu.column_name = %s 
                        AND tc.constraint_type = 'UNIQUE'
                    """, [table_name, col_name])
                    count = cursor.fetchone()[0]
                    return count > 0
                return False
        except Exception:
            return False
