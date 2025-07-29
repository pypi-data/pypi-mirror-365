import logging
from django.db import connections
from django.apps import apps
from .exceptions import DatabaseConnectionError

logger = logging.getLogger(__name__)

class DatabaseInspector:
    """Inspect database structure and compare with Django models"""
    
    def __init__(self, database_alias='default'):
        self.database_alias = database_alias
        self.connection = None
        self.cursor = None
        self._connect()
    
    def _connect(self):
        """Establish database connection"""
        try:
            self.connection = connections[self.database_alias]
            self.cursor = self.connection.cursor()
            logger.info(f"Connected to database: {self.database_alias}")
        except Exception as e:
            raise DatabaseConnectionError(f"Failed to connect to {self.database_alias}: {e}")
    
    def get_database_engine(self):
        """Get the database engine type"""
        return self.connection.vendor
    
    def get_existing_tables(self):
        """Get list of existing tables in database"""
        return self.connection.introspection.table_names()
    
    def get_table_description(self, table_name):
        """Get detailed column information for a table"""
        return self.connection.introspection.get_table_description(self.cursor, table_name)
    
    def get_table_constraints(self, table_name):
        """Get constraints for a table"""
        return self.connection.introspection.get_constraints(self.cursor, table_name)
    
    def get_foreign_key_constraints(self, table_name):
        """Get foreign key constraints for a table"""
        try:
            all_constraints = self.get_table_constraints(table_name)
            foreign_key_constraints = {}
            
            for constraint_name, constraint_info in all_constraints.items():
                # Check if this is a foreign key constraint
                if constraint_info.get('foreign_key'):
                    foreign_key_constraints[constraint_name] = {
                        'constrained_columns': constraint_info.get('columns', []),
                        'referred_table': constraint_info.get('foreign_key')[0] if constraint_info.get('foreign_key') else None,
                        'referred_columns': constraint_info.get('foreign_key')[1] if constraint_info.get('foreign_key') and len(constraint_info.get('foreign_key', [])) > 1 else []
                    }
            
            return foreign_key_constraints
            
        except Exception as e:
            logger.warning(f"Could not get foreign key constraints for {table_name}: {e}")
            return {}
    
    def get_table_indexes(self, table_name):
        """Get indexes for a table"""
        return self.connection.introspection.get_indexes(self.cursor, table_name)
    
    def get_database_info(self):
        """Get comprehensive database information"""
        tables = self.get_existing_tables()
        db_info = {
            'engine': self.get_database_engine(),
            'tables': {},
            'total_tables': len(tables)
        }
        
        for table in tables:
            try:
                description = self.get_table_description(table)
                constraints = self.get_table_constraints(table)
                
                db_info['tables'][table] = {
                    'columns': {col.name: {
                        'type': col.type_code,
                        'display_size': col.display_size,
                        'internal_size': col.internal_size,
                        'precision': col.precision,
                        'scale': col.scale,
                        'null_ok': col.null_ok,
                    } for col in description},
                    'constraints': constraints,
                }
            except Exception as e:
                logger.warning(f"Could not inspect table {table}: {e}")
                db_info['tables'][table] = {'error': str(e)}
        
        return db_info
    
    def close(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        # Django connections are managed automatically