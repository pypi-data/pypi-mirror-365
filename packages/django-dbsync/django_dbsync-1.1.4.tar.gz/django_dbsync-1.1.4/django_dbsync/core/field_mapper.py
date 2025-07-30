import logging
from django.db import models
from .exceptions import FieldMappingError

logger = logging.getLogger(__name__)

class FieldMapper:
    """Map Django fields to database-specific column definitions"""
    
    def __init__(self, database_engine):
        self.engine = database_engine.lower()
        self.type_mappings = self._get_type_mappings()
    
    def _get_type_mappings(self):
        """Get field type mappings for different database engines"""
        if self.engine == 'mysql':
            return self._get_mysql_mappings()
        elif self.engine == 'postgresql':
            return self._get_postgresql_mappings()
        elif self.engine == 'sqlite':
            return self._get_sqlite_mappings()
        else:
            raise FieldMappingError(f"Unsupported database engine: {self.engine}")
    
    def _get_mysql_mappings(self):
        """MySQL field type mappings"""
        return {
            'AutoField': lambda f: 'INT AUTO_INCREMENT',
            'BigAutoField': lambda f: 'BIGINT AUTO_INCREMENT',
            'CharField': lambda f: f'VARCHAR({getattr(f, "max_length", 255)})',
            'TextField': lambda f: 'TEXT',
            'IntegerField': lambda f: 'INT',
            'BigIntegerField': lambda f: 'BIGINT',
            'SmallIntegerField': lambda f: 'SMALLINT',
            'PositiveIntegerField': lambda f: 'INT UNSIGNED',
            'PositiveSmallIntegerField': lambda f: 'SMALLINT UNSIGNED',
            'FloatField': lambda f: 'FLOAT',
            'DecimalField': lambda f: f'DECIMAL({getattr(f, "max_digits", 10)},{getattr(f, "decimal_places", 2)})',
            'BooleanField': lambda f: 'BOOLEAN',
            'DateField': lambda f: 'DATE',
            'DateTimeField': lambda f: 'DATETIME',
            'TimeField': lambda f: 'TIME',
            'EmailField': lambda f: f'VARCHAR({getattr(f, "max_length", 254)})',
            'URLField': lambda f: f'VARCHAR({getattr(f, "max_length", 200)})',
            'SlugField': lambda f: f'VARCHAR({getattr(f, "max_length", 50)})',
            'ImageField': lambda f: f'VARCHAR({getattr(f, "max_length", 100)})',
            'FileField': lambda f: f'VARCHAR({getattr(f, "max_length", 100)})',
            'UUIDField': lambda f: 'CHAR(36)',
            'JSONField': lambda f: self._get_json_field_type(f),
            'DurationField': lambda f: 'BIGINT',  # Store as seconds
            'GenericIPAddressField': lambda f: 'VARCHAR(45)',  # IPv6 max length
            'BinaryField': lambda f: 'LONGBLOB',
            'ForeignKey': lambda f: self._get_foreign_key_type(f),
            'OneToOneField': lambda f: self._get_foreign_key_type(f),
        }
    
    def _get_postgresql_mappings(self):
        """PostgreSQL field type mappings"""
        return {
            'AutoField': lambda f: 'SERIAL',
            'BigAutoField': lambda f: 'BIGSERIAL',
            'CharField': lambda f: f'VARCHAR({getattr(f, "max_length", 255)})',
            'TextField': lambda f: 'TEXT',
            'IntegerField': lambda f: 'INTEGER',
            'BigIntegerField': lambda f: 'BIGINT',
            'SmallIntegerField': lambda f: 'SMALLINT',
            'PositiveIntegerField': lambda f: 'INTEGER CHECK (value >= 0)',
            'PositiveSmallIntegerField': lambda f: 'SMALLINT CHECK (value >= 0)',
            'FloatField': lambda f: 'REAL',
            'DecimalField': lambda f: f'DECIMAL({getattr(f, "max_digits", 10)},{getattr(f, "decimal_places", 2)})',
            'BooleanField': lambda f: 'BOOLEAN',
            'DateField': lambda f: 'DATE',
            'DateTimeField': lambda f: 'TIMESTAMP',
            'TimeField': lambda f: 'TIME',
            'EmailField': lambda f: f'VARCHAR({getattr(f, "max_length", 254)})',
            'URLField': lambda f: f'VARCHAR({getattr(f, "max_length", 200)})',
            'SlugField': lambda f: f'VARCHAR({getattr(f, "max_length", 50)})',
            'ImageField': lambda f: f'VARCHAR({getattr(f, "max_length", 100)})',
            'FileField': lambda f: f'VARCHAR({getattr(f, "max_length", 100)})',
            'UUIDField': lambda f: 'UUID',
            'JSONField': lambda f: 'JSONB',
            'ForeignKey': lambda f: self._get_foreign_key_type(f),
            'OneToOneField': lambda f: self._get_foreign_key_type(f),
        }
    
    def _get_sqlite_mappings(self):
        """SQLite field type mappings"""
        return {
            'AutoField': lambda f: 'INTEGER PRIMARY KEY AUTOINCREMENT',
            'BigAutoField': lambda f: 'INTEGER PRIMARY KEY AUTOINCREMENT',
            'CharField': lambda f: 'VARCHAR',
            'TextField': lambda f: 'TEXT',
            'IntegerField': lambda f: 'INTEGER',
            'BigIntegerField': lambda f: 'INTEGER',
            'SmallIntegerField': lambda f: 'INTEGER',
            'PositiveIntegerField': lambda f: 'INTEGER',
            'PositiveSmallIntegerField': lambda f: 'INTEGER',
            'FloatField': lambda f: 'REAL',
            'DecimalField': lambda f: 'DECIMAL',
            'BooleanField': lambda f: 'BOOLEAN',
            'DateField': lambda f: 'DATE',
            'DateTimeField': lambda f: 'DATETIME',
            'TimeField': lambda f: 'TIME',
            'EmailField': lambda f: 'VARCHAR',
            'URLField': lambda f: 'VARCHAR',
            'SlugField': lambda f: 'VARCHAR',
            'ImageField': lambda f: 'VARCHAR',
            'FileField': lambda f: 'VARCHAR',
            'UUIDField': lambda f: 'CHAR(36)',
            'JSONField': lambda f: 'TEXT',
            'ForeignKey': lambda f: self._get_foreign_key_type(f),
            'OneToOneField': lambda f: self._get_foreign_key_type(f),
        }
    
    def should_exclude_table(self, table_name: str) -> bool:
        """
        Check if a table should be excluded (Django system tables + custom patterns)
        """
        import re
        from ..settings import get_setting
        
        # If no-restriction mode is enabled, don't exclude any tables
        if hasattr(self, '_no_restriction') and self._no_restriction:
            logger.debug(f"No-restriction mode: not excluding table '{table_name}'")
            return False
        
        # Check Django system table prefixes
        system_table_prefixes = [
            'auth_',
            'django_',
            'contenttypes_',
            'sessions_',
            'admin_',
        ]
        
        # Check system tables
        for prefix in system_table_prefixes:
            if table_name.startswith(prefix):
                logger.debug(f"Excluding system table: {table_name} (matches prefix: {prefix})")
                return True
        
        # Check explicit table exclusions
        exclude_tables = get_setting('EXCLUDE_TABLES', [])
        if table_name in exclude_tables:
            logger.debug(f"Excluding table via EXCLUDE_TABLES: {table_name}")
            return True
        
        # Check regex pattern exclusions
        exclude_patterns = get_setting('EXCLUDE_TABLE_PATTERNS', [])
        
        # Add temporary patterns from command line if available via sync engine
        if hasattr(self, 'sync_engine') and hasattr(self.sync_engine, '_temp_exclude_table_patterns'):
            if self.sync_engine._temp_exclude_table_patterns:
                exclude_patterns.extend(self.sync_engine._temp_exclude_table_patterns)
        
        # Log all patterns being checked
        if exclude_patterns:
            logger.debug(f"Checking table '{table_name}' against exclusion patterns: {exclude_patterns}")
        
        for pattern in exclude_patterns:
            try:
                if re.match(pattern, table_name):
                    logger.debug(f"Excluding table '{table_name}' (matches pattern: {pattern})")
                    return True
            except re.error as e:
                logger.warning(f"Invalid regex pattern '{pattern}': {e}")
                continue
        
        logger.debug(f"Table '{table_name}' not excluded")
        return False
    
    def _get_foreign_key_type(self, field):
        """Get the correct data type for a foreign key column based on the referenced primary key"""
        try:
            # Get the related model and its primary key field
            related_model = field.related_model
            pk_field = related_model._meta.pk
            pk_field_type = type(pk_field).__name__
            
            # Map the primary key field type to the appropriate foreign key column type
            if self.engine == 'mysql':
                type_mapping = {
                    'AutoField': 'INT',
                    'BigAutoField': 'BIGINT',
                    'IntegerField': 'INT',
                    'BigIntegerField': 'BIGINT',
                    'SmallIntegerField': 'SMALLINT',
                    'PositiveIntegerField': 'INT UNSIGNED',
                    'PositiveSmallIntegerField': 'SMALLINT UNSIGNED',
                    'UUIDField': 'CHAR(36)',
                }
            elif self.engine == 'postgresql':
                type_mapping = {
                    'AutoField': 'INTEGER',
                    'BigAutoField': 'BIGINT',
                    'IntegerField': 'INTEGER',
                    'BigIntegerField': 'BIGINT',
                    'SmallIntegerField': 'SMALLINT',
                    'PositiveIntegerField': 'INTEGER',
                    'PositiveSmallIntegerField': 'SMALLINT',
                    'UUIDField': 'UUID',
                }
            elif self.engine == 'sqlite':
                # SQLite uses INTEGER for all integer types
                type_mapping = {
                    'AutoField': 'INTEGER',
                    'BigAutoField': 'INTEGER',
                    'IntegerField': 'INTEGER',
                    'BigIntegerField': 'INTEGER',
                    'SmallIntegerField': 'INTEGER',
                    'PositiveIntegerField': 'INTEGER',
                    'PositiveSmallIntegerField': 'INTEGER',
                    'UUIDField': 'CHAR(36)',
                }
            else:
                # Default fallback
                type_mapping = {
                    'AutoField': 'INTEGER',
                    'BigAutoField': 'BIGINT',
                    'IntegerField': 'INTEGER',
                    'BigIntegerField': 'BIGINT',
                    'SmallIntegerField': 'SMALLINT',
                    'UUIDField': 'CHAR(36)',
                }
            
            # Return the appropriate type or default to INTEGER
            return type_mapping.get(pk_field_type, 'INTEGER')
            
        except Exception as e:
            # Fallback to default type if we can't determine the referenced type
            if self.engine == 'mysql':
                return 'INT'
            else:
                return 'INTEGER'
    
    def _get_json_field_type(self, field):
        """Get the correct JSON field type based on database engine and field configuration"""
        try:
            # Handle default value for JSON fields
            default_value = getattr(field, 'default', None)
            
            if self.engine == 'mysql':
                # MySQL JSON field - always return JSON type, handle defaults separately
                return 'JSON'
            elif self.engine == 'postgresql':
                return 'JSONB'
            elif self.engine == 'sqlite':
                return 'TEXT'  # SQLite doesn't have native JSON, use TEXT
            else:
                return 'JSON'
                
        except Exception as e:
            # Fallback to safe default
            if self.engine == 'mysql':
                return 'JSON'
            elif self.engine == 'postgresql':
                return 'JSONB'
            else:
                return 'TEXT'

    def field_to_column_definition(self, field):
        """Convert Django field to database column definition"""
        field_type = type(field).__name__
        
        # Skip ManyToManyField - these are handled separately via intermediate tables
        if field_type == 'ManyToManyField':
            return None  # Signal that this field should be handled separately
        
        # Get base type
        mapper = self.type_mappings.get(field_type)
        if not mapper:
            raise FieldMappingError(f"Unsupported field type: {field_type}")
        
        base_type = mapper(field)
        
        # Add constraints
        constraints = []
        
        # NULL/NOT NULL - Special handling for foreign keys
        if field_type in ['ForeignKey', 'OneToOneField']:
            # Foreign keys should be nullable by default unless explicitly set to null=False
            is_nullable = getattr(field, 'null', True)  # Default to True for FK fields
            if is_nullable:
                constraints.append('NULL')
            else:
                constraints.append('NOT NULL')
        else:
            # Regular fields follow Django's default behavior
            if getattr(field, 'null', False):
                constraints.append('NULL')
            else:
                constraints.append('NOT NULL')
        
        # Default value handling
        if hasattr(field, 'default') and field.default != models.NOT_PROVIDED:
            if field.default is None:
                constraints.append('DEFAULT NULL')
            elif isinstance(field.default, str):
                constraints.append(f"DEFAULT '{field.default}'")
            elif isinstance(field.default, bool):
                default_val = 'TRUE' if field.default else 'FALSE'
                if self.engine == 'mysql':
                    default_val = '1' if field.default else '0'
                constraints.append(f'DEFAULT {default_val}')
            elif field_type == 'JSONField':
                # Handle JSON field defaults specially
                if callable(field.default):
                    # For callable defaults like dict, don't add DEFAULT constraint
                    # The default will be handled by Django
                    pass
                else:
                    # For literal JSON defaults
                    constraints.append(f"DEFAULT '{field.default}'")
            else:
                constraints.append(f'DEFAULT {field.default}')
        elif field_type in ['ForeignKey', 'OneToOneField']:
            # Foreign key fields should default to NULL unless explicitly set otherwise
            is_nullable = getattr(field, 'null', True)  # Default to True for FK fields
            if is_nullable:
                constraints.append('DEFAULT NULL')
        
        # Primary key (for non-auto fields)
        if getattr(field, 'primary_key', False) and 'AUTO' not in base_type.upper():
            constraints.append('PRIMARY KEY')
        
        # Unique constraint
        if getattr(field, 'unique', False):
            constraints.append('UNIQUE')
        
        return f"{base_type} {' '.join(constraints)}".strip()