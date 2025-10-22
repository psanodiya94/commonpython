"""
Manager Factory for CommonPython Framework

Factory class for creating database and messaging manager instances based on
configuration. Supports automatic selection between CLI and library implementations
with intelligent fallback mechanisms.
"""

from typing import Any, Dict

from ..interfaces.database_interface import IDatabaseManager
from ..interfaces.messaging_interface import IMessagingManager


class ManagerFactory:
    """
    Factory for creating manager instances based on configuration.

    Provides static methods to create database and messaging managers
    with automatic selection of implementation type (CLI or library)
    based on configuration and availability.
    """

    # Cache for adapter availability checks
    _adapter_cache = {"db2_library_available": None, "mq_library_available": None}

    @staticmethod
    def create_database_manager(config: Dict[str, Any], logger=None) -> IDatabaseManager:
        """
        Create database manager based on configuration.

        @brief Create database manager with automatic implementation selection.
        @param config Database configuration dictionary
        @param logger Logger manager instance (optional)
        @return IDatabaseManager implementation instance
        @throws ValueError If specified implementation is not available
        @throws ImportError If required dependencies are missing

        Configuration keys:
        - implementation: 'cli' or 'library' (default: 'cli')
        - auto_fallback: True to automatically fallback to CLI if library unavailable (default: True)
        """
        impl_type = config.get("implementation", "cli").lower()
        auto_fallback = config.get("auto_fallback", True)

        # Check library adapter availability (cached)
        if ManagerFactory._adapter_cache["db2_library_available"] is None:
            try:
                from ..adapters.db2_library_adapter import HAS_IBM_DB, DB2LibraryAdapter

                ManagerFactory._adapter_cache["db2_library_available"] = HAS_IBM_DB
            except ImportError:
                ManagerFactory._adapter_cache["db2_library_available"] = False

        if impl_type == "library":
            if ManagerFactory._adapter_cache["db2_library_available"]:
                from ..adapters.db2_library_adapter import DB2LibraryAdapter

                if logger:
                    logger.logger.info("Using DB2 library adapter (ibm_db)")
                return DB2LibraryAdapter(config, logger)
            elif auto_fallback:
                if logger:
                    logger.logger.warning(
                        "DB2 library adapter not available (ibm_db not installed), "
                        "falling back to CLI adapter"
                    )
                from ..adapters.db2_cli_adapter import DB2CLIAdapter

                return DB2CLIAdapter(config, logger)
            else:
                raise ValueError(
                    "DB2 library implementation requested but ibm_db is not installed. "
                    "Install with: pip install ibm_db"
                )

        elif impl_type == "cli":
            from ..adapters.db2_cli_adapter import DB2CLIAdapter

            if logger:
                logger.logger.info("Using DB2 CLI adapter")
            return DB2CLIAdapter(config, logger)

        else:
            raise ValueError(
                f"Unknown database implementation type: '{impl_type}'. "
                f"Valid options are 'cli' or 'library'"
            )

    @staticmethod
    def create_messaging_manager(config: Dict[str, Any], logger=None) -> IMessagingManager:
        """
        Create messaging manager based on configuration.

        @brief Create messaging manager with automatic implementation selection.
        @param config Messaging configuration dictionary
        @param logger Logger manager instance (optional)
        @return IMessagingManager implementation instance
        @throws ValueError If specified implementation is not available
        @throws ImportError If required dependencies are missing

        Configuration keys:
        - implementation: 'cli' or 'library' (default: 'cli')
        - auto_fallback: True to automatically fallback to CLI if library unavailable (default: True)
        """
        impl_type = config.get("implementation", "cli").lower()
        auto_fallback = config.get("auto_fallback", True)

        # Check library adapter availability (cached)
        if ManagerFactory._adapter_cache["mq_library_available"] is None:
            try:
                from ..adapters.mq_library_adapter import HAS_PYMQI, MQLibraryAdapter

                ManagerFactory._adapter_cache["mq_library_available"] = HAS_PYMQI
            except ImportError:
                ManagerFactory._adapter_cache["mq_library_available"] = False

        if impl_type == "library":
            if ManagerFactory._adapter_cache["mq_library_available"]:
                from ..adapters.mq_library_adapter import MQLibraryAdapter

                if logger:
                    logger.logger.info("Using MQ library adapter (pymqi)")
                return MQLibraryAdapter(config, logger)
            elif auto_fallback:
                if logger:
                    logger.logger.warning(
                        "MQ library adapter not available (pymqi not installed), "
                        "falling back to CLI adapter"
                    )
                from ..adapters.mq_cli_adapter import MQCLIAdapter

                return MQCLIAdapter(config, logger)
            else:
                raise ValueError(
                    "MQ library implementation requested but pymqi is not installed. "
                    "Install with: pip install pymqi"
                )

        elif impl_type == "cli":
            from ..adapters.mq_cli_adapter import MQCLIAdapter

            if logger:
                logger.logger.info("Using MQ CLI adapter")
            return MQCLIAdapter(config, logger)

        else:
            raise ValueError(
                f"Unknown messaging implementation type: '{impl_type}'. "
                f"Valid options are 'cli' or 'library'"
            )

    @staticmethod
    def get_available_implementations() -> Dict[str, Dict[str, bool]]:
        """
        Get information about available implementations.

        @brief Check which implementations are available.
        @return Dictionary with availability information for each manager type

        Example return:
        {
            'database': {
                'cli': True,
                'library': False  # ibm_db not installed
            },
            'messaging': {
                'cli': True,
                'library': True
            }
        }
        """
        # Check DB2 library
        try:
            from ..adapters.db2_library_adapter import HAS_IBM_DB, DB2LibraryAdapter

            db2_library_available = HAS_IBM_DB
        except ImportError:
            db2_library_available = False

        # Check MQ library
        try:
            from ..adapters.mq_library_adapter import HAS_PYMQI, MQLibraryAdapter

            mq_library_available = HAS_PYMQI
        except ImportError:
            mq_library_available = False

        return {
            "database": {
                "cli": True,  # CLI adapter is always available
                "library": db2_library_available,
            },
            "messaging": {
                "cli": True,  # CLI adapter is always available
                "library": mq_library_available,
            },
        }

    @staticmethod
    def reset_cache():
        """
        Reset the adapter availability cache.

        @brief Reset cached availability information.
        Useful for testing or when dependencies are installed at runtime.
        """
        ManagerFactory._adapter_cache = {
            "db2_library_available": None,
            "mq_library_available": None,
        }
