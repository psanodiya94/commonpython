"""
MQ CLI Adapter for CommonPython Framework

Adapter that wraps the CLI-based MQManager implementation and implements
the IMessagingManager interface. This allows the CLI implementation to be
used interchangeably with library-based implementations.
"""

from typing import Any, Dict, Optional, Union
from ..interfaces.messaging_interface import IMessagingManager
from ..messaging.mq_manager import MQManager


class MQCLIAdapter(IMessagingManager):
    """
    Adapter for CLI-based MQ messaging operations.

    Wraps the existing MQManager (CLI-based) implementation and exposes
    it through the IMessagingManager interface.
    """

    def __init__(self, config: Dict[str, Any], logger=None):
        """
        Initialize the MQ CLI adapter.

        @brief Initialize adapter with CLI-based MQManager.
        @param config Messaging configuration dictionary
        @param logger Logger manager instance (optional)
        """
        self._impl = MQManager(config, logger)
        self._config = config
        self._logger = logger

    def connect(self) -> bool:
        """
        Establish connection to MQ queue manager using CLI.

        @brief Connect to messaging server via CLI tools.
        @return True if connection successful, False otherwise
        """
        return self._impl.connect()

    def disconnect(self) -> None:
        """
        Close the messaging connection.

        @brief Disconnect from messaging server via CLI tools.
        """
        self._impl.disconnect()

    def is_connected(self) -> bool:
        """
        Check if messaging connection is active.

        @brief Check CLI connection status.
        @return True if connected, False otherwise
        """
        return self._impl.is_connected()

    def put_message(self, queue_name: str, message: Union[str, bytes, Dict],
                   message_properties: Optional[Dict[str, Any]] = None) -> bool:
        """
        Put a message to a queue.

        @brief Send message to queue via CLI tools.
        @param queue_name Name of the queue
        @param message Message content (string, bytes, or dictionary)
        @param message_properties Optional message properties
        @return True if message sent successfully, False otherwise
        @throws Exception If message sending fails
        """
        return self._impl.put_message(queue_name, message, message_properties)

    def get_message(self, queue_name: str, timeout: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Get a message from a queue.

        @brief Receive message from queue via CLI tools.
        @param queue_name Name of the queue
        @param timeout Timeout in seconds (None for default timeout)
        @return Dictionary containing message data and properties, or None if no message
        @throws Exception If message retrieval fails
        """
        return self._impl.get_message(queue_name, timeout)

    def browse_message(self, queue_name: str, message_id: Optional[bytes] = None) -> Optional[Dict[str, Any]]:
        """
        Browse a message from a queue without removing it.

        @brief Browse message via CLI tools.
        @param queue_name Name of the queue
        @param message_id Specific message ID to browse (optional)
        @return Dictionary containing message data and properties, or None if no message
        @throws Exception If message browsing fails
        """
        return self._impl.browse_message(queue_name, message_id)

    def get_queue_depth(self, queue_name: str) -> int:
        """
        Get the depth (number of messages) in a queue.

        @brief Get queue depth via CLI tools.
        @param queue_name Name of the queue
        @return Number of messages in the queue, -1 if error
        @throws Exception If queue depth retrieval fails
        """
        return self._impl.get_queue_depth(queue_name)

    def purge_queue(self, queue_name: str) -> int:
        """
        Purge all messages from a queue.

        @brief Purge queue via CLI tools.
        @param queue_name Name of the queue
        @return Number of messages purged
        @throws Exception If queue purging fails
        """
        return self._impl.purge_queue(queue_name)

    def test_connection(self) -> bool:
        """
        Test messaging connection.

        @brief Test CLI messaging connection.
        @return True if connection is working, False otherwise
        """
        return self._impl.test_connection()
