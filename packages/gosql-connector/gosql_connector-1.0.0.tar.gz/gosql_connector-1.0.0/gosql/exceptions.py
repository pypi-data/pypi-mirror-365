"""
GoSQL Exception Classes

This module defines all exception classes used by GoSQL, maintaining compatibility
with Python database API 2.0 (PEP 249) and popular database connectors.
"""

class GoSQLError(Exception):
    """Base exception class for all GoSQL errors."""
    
    def __init__(self, message, errno=None, sqlstate=None):
        super().__init__(message)
        self.errno = errno
        self.sqlstate = sqlstate
        self.message = message
    
    def __str__(self):
        if self.errno and self.sqlstate:
            return f"{self.errno} ({self.sqlstate}): {self.message}"
        elif self.errno:
            return f"{self.errno}: {self.message}"
        else:
            return self.message


class Warning(GoSQLError):
    """Exception raised for important warnings like data truncations."""
    pass


class Error(GoSQLError):
    """Base class for all database errors."""
    pass


class InterfaceError(Error):
    """Exception raised for errors related to the database interface."""
    pass


class DatabaseError(Error):
    """Exception raised for errors related to the database."""
    pass


class DataError(DatabaseError):
    """Exception raised for errors due to problems with the processed data."""
    pass


class OperationalError(DatabaseError):
    """Exception raised for errors related to database operation."""
    pass


class IntegrityError(DatabaseError):
    """Exception raised when the relational integrity of the database is affected."""
    pass


class InternalError(DatabaseError):
    """Exception raised when the database encounters an internal error."""
    pass


class ProgrammingError(DatabaseError):
    """Exception raised for programming errors."""
    pass


class NotSupportedError(DatabaseError):
    """Exception raised for operations not supported by the database."""
    pass


class ConnectionError(OperationalError):
    """Exception raised for connection-related errors."""
    pass


class TimeoutError(OperationalError):
    """Exception raised when an operation times out."""
    pass


class PoolError(OperationalError):
    """Exception raised for connection pool related errors."""
    pass


# MySQL-specific exceptions for compatibility
class MySQLError(GoSQLError):
    """Base exception for MySQL-specific errors."""
    pass


class MySQLInterfaceError(InterfaceError, MySQLError):
    """MySQL interface error."""
    pass


class MySQLDatabaseError(DatabaseError, MySQLError):
    """MySQL database error."""
    pass


# PostgreSQL-specific exceptions for compatibility  
class PostgreSQLError(GoSQLError):
    """Base exception for PostgreSQL-specific errors."""
    pass


class PostgreSQLInterfaceError(InterfaceError, PostgreSQLError):
    """PostgreSQL interface error."""
    pass


class PostgreSQLDatabaseError(DatabaseError, PostgreSQLError):
    """PostgreSQL database error."""
    pass


# SQL Server-specific exceptions for compatibility
class SQLServerError(GoSQLError):
    """Base exception for SQL Server-specific errors."""
    pass


class SQLServerInterfaceError(InterfaceError, SQLServerError):
    """SQL Server interface error."""
    pass


class SQLServerDatabaseError(DatabaseError, SQLServerError):
    """SQL Server database error."""
    pass


# Error mapping for different database types
ERROR_MAPPING = {
    'mysql': {
        'base': MySQLError,
        'interface': MySQLInterfaceError,
        'database': MySQLDatabaseError,
    },
    'postgresql': {
        'base': PostgreSQLError,
        'interface': PostgreSQLInterfaceError, 
        'database': PostgreSQLDatabaseError,
    },
    'mssql': {
        'base': SQLServerError,
        'interface': SQLServerInterfaceError,
        'database': SQLServerDatabaseError,
    }
}


def get_exception_class(db_type, error_type='base'):
    """
    Get the appropriate exception class for a database type.
    
    Args:
        db_type: Database type ('mysql', 'postgresql', 'mssql')
        error_type: Error type ('base', 'interface', 'database')
    
    Returns:
        Exception class
    """
    return ERROR_MAPPING.get(db_type, {}).get(error_type, GoSQLError)


def create_error_from_go(error_code, error_message, db_type='mysql'):
    """
    Create appropriate Python exception from Go error.
    
    Args:
        error_code: Error code from Go
        error_message: Error message from Go
        db_type: Database type
    
    Returns:
        Appropriate exception instance
    """
    # Map common error codes to exception types
    if error_code in [1045, 2003, 2013]:  # Authentication/connection errors
        return ConnectionError(error_message, error_code)
    elif error_code in [1146, 1054]:  # Table/column doesn't exist
        return ProgrammingError(error_message, error_code)
    elif error_code in [1062, 1586]:  # Duplicate entry/integrity constraint
        return IntegrityError(error_message, error_code)
    elif error_code in [1264, 1406]:  # Data truncation/too long
        return DataError(error_message, error_code)
    else:
        # Default to database error
        error_class = get_exception_class(db_type, 'database')
        return error_class(error_message, error_code)


# Exception hierarchy for documentation
EXCEPTION_HIERARCHY = """
GoSQL Exception Hierarchy:

GoSQLError
 +-- Warning
 +-- Error
      +-- InterfaceError
      +-- DatabaseError
           +-- DataError
           +-- OperationalError
           |    +-- ConnectionError
           |    +-- TimeoutError
           |    +-- PoolError
           +-- IntegrityError
           +-- InternalError
           +-- ProgrammingError
           +-- NotSupportedError

Database-specific exceptions inherit from both base exceptions and database-specific base classes.
"""
