import logging
from datetime import datetime
from django.apps import apps
from django.db import connections, models, transaction
from django.conf import settings

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
            
            for model in app_config.get_models():
                models_list.append(model)
        
        return models_list
    
    def get_table_name(self, model):
        """Get the actual table name for a model"""
        return model._meta.db_table
    
    def get_default_table_name(self, model):
        """Get the default Django table name"""
        return f"{model._meta.app_label}_{model._meta.model_name}"
    
    def find_existing_table_for_model(self, model):
        """Find existing table that matches the model"""
        expected_table = self.get_table_name(model)
        default_table = self.get_default_table_name(model)
        existing_tables = self.inspector.get_existing_tables()
        
        # Check if expected table exists
        if expected_table in existing_tables:
            return expected_table, None
        
        # Check if default table exists (rename scenario)
        if default_table in existing_tables and default_table != expected_table:
            return default_table, expected_table
        
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
        
        # Check if this table should be excluded
        if self.field_mapper.should_exclude_table(table_name):
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
            
            # Handle table creation or renaming
            table_was_created = False
            if not existing_table:
                # Create new table
                if self._create_table(model, target_table_name):
                    result['actions'].append(f"Created table '{target_table_name}'")
                    table_was_created = True
                    existing_table = target_table_name  # Set for further processing
            
            # Handle table renaming
            if rename_target and existing_table != rename_target:
                if self._should_rename_table(existing_table, rename_target):
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
            
            # Sync columns (only if table wasn't just created)
            if not table_was_created:
                working_table = existing_table if existing_table else target_table_name
                column_results = self._sync_columns(model, working_table)
                result['actions'].extend(column_results['actions'])
                result['warnings'].extend(column_results['warnings'])
                result['errors'].extend(column_results['errors'])
            else:
                # Table was just created, no need for column sync
                column_results = {'actions': [], 'warnings': [], 'errors': []}
        
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
            logger.error(f"Error syncing model {model_name}: {e}")
            result['status'] = 'error'
            result['errors'].append(str(e))
        
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
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Would ask to rename '{old_name}' to '{new_name}'")
            return True
        
        response = input(f"Rename table '{old_name}' to '{new_name}'? (y/N): ")
        return response.lower() == 'y'
    
    def _rename_table(self, old_name, new_name):
        """Rename a table"""
        if self.dry_run:
            logger.info(f"[DRY RUN] Would rename table: {old_name} -> {new_name}")
            return True
        
        try:
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
                    logger.info(f"Checking column '{col_name}' in '{table_name}' - field type: {field_type}")
                    
                    if field_type in ['ForeignKey', 'OneToOneField']:
                        logger.info(f"Found foreign key field '{col_name}' in '{table_name}' - checking if fix needed")
                        # Only check and fix if constraint is actually missing
                        if not self._check_foreign_key_constraint_exists(table_name, col_name, field):
                            logger.info(f"Foreign key constraint missing for '{col_name}' in '{table_name}' - attempting to fix")
                            if self._fix_existing_foreign_key_column(table_name, col_name, field):
                                result['actions'].append(f"Fixed foreign key column '{col_name}' in '{table_name}'")
                            else:
                                result['warnings'].append(f"Could not fully fix foreign key column '{col_name}' in '{table_name}'")
                        else:
                            logger.debug(f"Foreign key constraint already exists for '{col_name}' in '{table_name}' - no fix needed")
            
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
            
            # Generate shorter constraint name to avoid MySQL 64-char limit
            import hashlib
            name_hash = hashlib.md5(f"{table_name}_{col_name}_{related_table}".encode()).hexdigest()[:8]
            constraint_name = f"fk_{table_name}_{col_name}_{name_hash}"
            
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
    
    def _fix_existing_foreign_key_column(self, table_name, col_name, field):
        """Fix existing foreign key column that may have wrong default or missing constraint"""
        logger.info(f"Starting _fix_existing_foreign_key_column for '{col_name}' in '{table_name}'")
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Would fix foreign key column '{col_name}' in '{table_name}'")
            return True
        
        fixed_something = False
        
        try:
            engine = self.inspector.get_database_engine()
            logger.info(f"Database engine: {engine}")
            
            # Check if foreign key constraint already exists
            logger.info(f"Checking if foreign key constraint exists for '{col_name}' in '{table_name}'")
            has_constraint = self._check_foreign_key_constraint_exists(table_name, col_name, field)
            logger.info(f"Foreign key constraint exists: {has_constraint}")
            
            if not has_constraint:
                logger.info(f"No foreign key constraint found, attempting to add one for '{col_name}' in '{table_name}'")
                # Add missing foreign key constraint
                if self._add_foreign_key_constraint(table_name, col_name, field):
                    logger.info(f"Successfully added missing foreign key constraint for '{col_name}' in '{table_name}'")
                    fixed_something = True
                else:
                    logger.error(f"Failed to add foreign key constraint for '{col_name}' in '{table_name}'")
            
            # Only report as "fixed" if we actually added a missing constraint
            # Skip column definition changes for now to avoid repetitive messages
            
            return fixed_something
            
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
            
            # Create table SQL
            engine = self.inspector.get_database_engine()
            if engine == 'mysql':
                create_query = f"""
                CREATE TABLE `{table_name}` (
                    `id` INT AUTO_INCREMENT PRIMARY KEY,
                    `{source_column}` {source_pk_type} NOT NULL,
                    `{target_column}` {target_pk_type} NOT NULL,
                    UNIQUE KEY `{table_name}_{source_column}_{target_column}_unique` (`{source_column}`, `{target_column}`),
                    KEY `{table_name}_{source_column}_idx` (`{source_column}`),
                    KEY `{table_name}_{target_column}_idx` (`{target_column}`),
                    CONSTRAINT `{table_name}_{source_column}_fk` FOREIGN KEY (`{source_column}`) REFERENCES `{source_model._meta.db_table}` (`id`) ON DELETE CASCADE,
                    CONSTRAINT `{table_name}_{target_column}_fk` FOREIGN KEY (`{target_column}`) REFERENCES `{target_model._meta.db_table}` (`id`) ON DELETE CASCADE
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
        """Get the exact column type from the database"""
        try:
            engine = self.inspector.get_database_engine()
            
            if engine == 'mysql':
                self.inspector.cursor.execute(f"""
                    SELECT COLUMN_TYPE
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_SCHEMA = DATABASE()
                    AND TABLE_NAME = %s
                    AND COLUMN_NAME = %s
                """, (table_name, column_name))
                
                result = self.inspector.cursor.fetchone()
                if result:
                    return result[0].upper()  # Return uppercase for consistency
                    
            elif engine == 'postgresql':
                self.inspector.cursor.execute(f"""
                    SELECT data_type
                    FROM information_schema.columns
                    WHERE table_name = %s AND column_name = %s
                """, (table_name, column_name))
                
                result = self.inspector.cursor.fetchone()
                if result:
                    return result[0].upper()
                    
            elif engine == 'sqlite':
                self.inspector.cursor.execute(f"PRAGMA table_info({table_name})")
                columns = self.inspector.cursor.fetchall()
                for col in columns:
                    if col[1] == column_name:  # col[1] is column name
                        return col[2].upper()  # col[2] is column type
            
            # Fallback to default type if not found
            logger.warning(f"Could not determine exact type for {table_name}.{column_name}, using BIGINT")
            return 'BIGINT'
            
        except Exception as e:
            logger.error(f"Error getting column type for {table_name}.{column_name}: {e}")
            return 'BIGINT'  # Safe fallback
    
    def _check_foreign_key_constraint_exists(self, table_name, col_name, field):
        """Check if a foreign key constraint already exists for this column"""
        try:
            engine = self.inspector.get_database_engine()
            
            if engine == 'mysql':
                self.inspector.cursor.execute(f"""
                    SELECT CONSTRAINT_NAME
                    FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                    WHERE TABLE_SCHEMA = DATABASE()
                    AND TABLE_NAME = %s
                    AND COLUMN_NAME = %s
                    AND REFERENCED_TABLE_NAME IS NOT NULL
                """, (table_name, col_name))
                
                return len(self.inspector.cursor.fetchall()) > 0
            
            elif engine == 'postgresql':
                self.inspector.cursor.execute("""
                    SELECT conname
                    FROM pg_constraint
                    WHERE contype = 'f'
                    AND conrelid = %s::regclass
                    AND %s = ANY(SELECT attname FROM pg_attribute 
                                WHERE attrelid = conrelid 
                                AND attnum = ANY(conkey))
                """, (table_name, col_name))
                
                return len(self.inspector.cursor.fetchall()) > 0
            
            return False
            
        except Exception as e:
            logger.warning(f"Error checking foreign key constraint for {table_name}.{col_name}: {e}")
            return False
    
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
        for model in models_list:
            expected_table = self.get_table_name(model)
            default_table = self.get_default_table_name(model)
            model_tables.add(expected_table)
            model_tables.add(default_table)
            
            # Add ManyToMany intermediate table names
            for field in model._meta.get_fields():
                if type(field).__name__ == 'ManyToManyField':
                    try:
                        through_model = field.remote_field.through
                        if through_model._meta.auto_created:
                            intermediate_table = through_model._meta.db_table
                            model_tables.add(intermediate_table)
                            logger.debug(f"Added M2M intermediate table to expected tables: {intermediate_table}")
                    except Exception as e:
                        logger.warning(f"Error processing M2M field {field.name} for orphaned table detection: {e}")
        
        # Find orphaned tables with details
        orphaned_tables = []
        for table in existing_tables:
            if table not in model_tables:
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
