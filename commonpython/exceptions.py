"""
Custom Exceptions for CommonPython Framework

Provides a hierarchy of custom exceptions for better error handling and debugging.
All exceptions inherit from a base CommonPythonError class.
"""


class CommonPythonError(Exception):
    """
    Base exception class for all CommonPython framework errors.

    @brief Base exception for CommonPython framework.
    """

    def __init__(self, message: str, details: dict = None):
        """
        Initialize the exception.

        @brief Initialize exception with message and optional details.
        @param message Error message
        @param details Optional dictionary with additional error context
        """
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self) -> str:
        """String representation of the exception."""
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            return f"{self.message} ({details_str})"
        return self.message


# Configuration Exceptions


class ConfigurationError(CommonPythonError):
    """
    Exception raised for configuration-related errors.

    @brief Configuration errors (invalid config, missing keys, etc.)
    """

    pass


class ConfigFileNotFoundError(ConfigurationError):
    """
    Exception raised when configuration file is not found.

    @brief Configuration file not found error.
    """

    pass


class ConfigValidationError(ConfigurationError):
    """
    Exception raised when configuration validation fails.

    @brief Configuration validation error.
    """

    pass


# Database Exceptions


class DatabaseError(CommonPythonError):
    """
    Base exception for all database-related errors.

    @brief Base database error.
    """

    pass


class DatabaseConnectionError(DatabaseError):
    """
    Exception raised when database connection fails.

    @brief Database connection error.
    """

    pass


class DatabaseQueryError(DatabaseError):
    """
    Exception raised when database query execution fails.

    @brief Database query execution error.
    """

    pass


class DatabaseTransactionError(DatabaseError):
    """
    Exception raised when database transaction fails.

    @brief Database transaction error.
    """

    pass


# Messaging Exceptions


class MessagingError(CommonPythonError):
    """
    Base exception for all messaging-related errors.

    @brief Base messaging error.
    """

    pass


class MessagingConnectionError(MessagingError):
    """
    Exception raised when messaging connection fails.

    @brief Messaging connection error.
    """

    pass


class MessageSendError(MessagingError):
    """
    Exception raised when message sending fails.

    @brief Message send error.
    """

    pass


class MessageReceiveError(MessagingError):
    """
    Exception raised when message receiving fails.

    @brief Message receive error.
    """

    pass


class QueueNotFoundError(MessagingError):
    """
    Exception raised when specified queue is not found.

    @brief Queue not found error.
    """

    pass


# Logging Exceptions


class LoggingError(CommonPythonError):
    """
    Exception raised for logging-related errors.

    @brief Logging configuration or operation error.
    """

    pass


# Adapter Exceptions


class AdapterError(CommonPythonError):
    """
    Base exception for adapter-related errors.

    @brief Base adapter error.
    """

    pass


class AdapterNotAvailableError(AdapterError):
    """
    Exception raised when requested adapter is not available.

    @brief Adapter not available (e.g., library not installed).
    """

    pass


class AdapterInitializationError(AdapterError):
    """
    Exception raised when adapter initialization fails.

    @brief Adapter initialization error.
    """

    pass


# Component Exceptions


class ComponentError(CommonPythonError):
    """
    Base exception for component-related errors.

    @brief Base component error.
    """

    pass


class ComponentInitializationError(ComponentError):
    """
    Exception raised when component initialization fails.

    @brief Component initialization error.
    """

    pass


class ComponentExecutionError(ComponentError):
    """
    Exception raised when component execution fails.

    @brief Component execution error.
    """

    pass


# CLI Exceptions


class CLIError(CommonPythonError):
    """
    Exception raised for CLI-related errors.

    @brief CLI execution or argument parsing error.
    """

    pass


class CLICommandError(CLIError):
    """
    Exception raised when CLI command execution fails.

    @brief CLI command execution error.
    """

    pass


# Validation Exceptions


class ValidationError(CommonPythonError):
    """
    Exception raised for validation errors.

    @brief Data validation error.
    """

    pass


class InvalidParameterError(ValidationError):
    """
    Exception raised when invalid parameter is provided.

    @brief Invalid parameter error.
    """

    pass


class MissingParameterError(ValidationError):
    """
    Exception raised when required parameter is missing.

    @brief Missing required parameter error.
    """

    pass


# Timeout Exceptions


class TimeoutError(CommonPythonError):
    """
    Exception raised when operation times out.

    @brief Operation timeout error.
    """

    pass


class DatabaseTimeoutError(TimeoutError):
    """
    Exception raised when database operation times out.

    @brief Database operation timeout.
    """

    pass


class MessagingTimeoutError(TimeoutError):
    """
    Exception raised when messaging operation times out.

    @brief Messaging operation timeout.
    """

    pass


# Exception Mapping for Migration


EXCEPTION_MAP = {
    "FileNotFoundError": ConfigFileNotFoundError,
    "KeyError": ConfigurationError,
    "ValueError": ValidationError,
    "ConnectionError": DatabaseConnectionError,
}


def map_exception(original_exception: Exception, message: str = None) -> CommonPythonError:
    """
    Map standard Python exceptions to CommonPython custom exceptions.

    @brief Convert standard exceptions to custom exceptions.
    @param original_exception Original exception instance
    @param message Optional custom message
    @return Mapped CommonPython exception

    Example:
        >>> try:
        ...     open('missing.txt')
        ... except FileNotFoundError as e:
        ...     raise map_exception(e, "Configuration file not found")
    """
    exc_type = type(original_exception).__name__
    custom_exc_class = EXCEPTION_MAP.get(exc_type, CommonPythonError)

    error_message = message or str(original_exception)
    return custom_exc_class(error_message, details={"original_error": str(original_exception)})
