"""
GoSQL - High-Performance Database Connector Library

A high-performance database connector library written in Go and designed for Python applications.
Provides unified database connectivity for MySQL, PostgreSQL, and Microsoft SQL Server with 
2-3x better performance than native Python connectors while maintaining 100% API compatibility.

Author: CoffeeCMS Team
License: MIT
Website: https://github.com/coffeecms/gosql
"""

__version__ = "1.0.0"
__author__ = "CoffeeCMS Team"
__email__ = "dev@coffeecms.com"
__license__ = "MIT"
__copyright__ = "Copyright 2024-2025 CoffeeCMS Team"
__url__ = "https://github.com/coffeecms/gosql"
__description__ = "High-performance Go-based SQL connector library for Python with 2-3x better performance"

# Version info tuple for programmatic access
VERSION_INFO = tuple(int(x) for x in __version__.split('.'))

# Expose main connection functions
from .mysql import connect as mysql_connect
from .postgres import connect as postgres_connect  
from .mssql import connect as mssql_connect

# Expose common exceptions
from .exceptions import (
    GoSQLError,
    ConnectionError,
    OperationalError,
    DatabaseError,
    InterfaceError,
    DataError,
    IntegrityError,
    InternalError,
    ProgrammingError,
    NotSupportedError
)

# Performance monitoring
from .core.performance import PerformanceMonitor

# Package metadata
__all__ = [
    # Version info
    "__version__",
    "__author__", 
    "__email__",
    "__license__",
    "__copyright__",
    "__url__",
    "__description__",
    "VERSION_INFO",
    
    # Connection functions
    "mysql_connect",
    "postgres_connect", 
    "mssql_connect",
    
    # Exceptions
    "GoSQLError",
    "ConnectionError",
    "OperationalError", 
    "DatabaseError",
    "InterfaceError",
    "DataError",
    "IntegrityError",
    "InternalError",
    "ProgrammingError",
    "NotSupportedError",
    
    # Performance monitoring
    "PerformanceMonitor"
]

# Package initialization
def get_version():
    """Get the current version of GoSQL."""
    return __version__

def get_build_info():
    """Get build information."""
    import os
    import platform
    
    return {
        "version": __version__,
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "architecture": platform.architecture()[0],
        "go_version": "1.21+",  # Minimum required Go version
        "build_date": "2025-01-01",  # Will be set during build
    }

# Initialize performance monitor
performance_monitor = PerformanceMonitor()

# Banner for CLI tools
BANNER = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   ██████╗  ██████╗ ███████╗ ██████╗ ██╗                                      ║
║  ██╔════╝ ██╔═══██╗██╔════╝██╔═══██╗██║                                      ║
║  ██║  ███╗██║   ██║███████╗██║   ██║██║                                      ║
║  ██║   ██║██║   ██║╚════██║██║▄▄ ██║██║                                      ║
║  ╚██████╔╝╚██████╔╝███████║╚██████╔╝███████╗                                 ║
║   ╚═════╝  ╚═════╝ ╚══════╝ ╚══▀▀═╝ ╚══════╝                                 ║
║                                                                              ║
║  High-Performance Database Connector Library                                ║
║  Version: {__version__:<20} License: {__license__:<10}                              ║
║  Performance: 2-3x faster than native Python connectors                    ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

# Show banner on import in development mode
if __name__ == "__main__":
    print(BANNER)
    print(f"GoSQL {__version__} - Ready for high-performance database operations!")
