"""
Adapters for CommonPython Framework

Provides adapter implementations for different database and messaging backends.
Adapters implement the abstract interfaces and wrap actual implementations.
"""

from .db2_cli_adapter import DB2CLIAdapter
from .mq_cli_adapter import MQCLIAdapter

# Library adapters may not be available if dependencies aren't installed
try:
    from .db2_library_adapter import DB2LibraryAdapter

    HAS_DB2_LIBRARY = True
except ImportError:
    HAS_DB2_LIBRARY = False

try:
    from .mq_library_adapter import MQLibraryAdapter

    HAS_MQ_LIBRARY = True
except ImportError:
    HAS_MQ_LIBRARY = False

__all__ = ["DB2CLIAdapter", "MQCLIAdapter"]

if HAS_DB2_LIBRARY:
    __all__.append("DB2LibraryAdapter")

if HAS_MQ_LIBRARY:
    __all__.append("MQLibraryAdapter")
