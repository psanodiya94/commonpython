"""
Messaging Interface for CommonPython Framework

Defines the abstract interface for messaging operations that all messaging
adapters must implement. This allows switching between CLI-based and
library-based implementations without changing client code.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union


class IMessagingManager(ABC):
    """
    Abstract interface for messaging management operations.

    All messaging adapters (CLI-based, library-based) must implement this interface
    to ensure compatibility with the CommonPython framework.
    """

    @abstractmethod
    def connect(self) -> bool:
        """
        Establish connection to the message queue manager.

        @brief Connect to messaging server.
        @return True if connection successful, False otherwise
        """
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """
        Close the messaging connection.

        @brief Disconnect from messaging server.
        """
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        """
        Check if messaging connection is active.

        @brief Check connection status.
        @return True if connected, False otherwise
        """
        pass

    @abstractmethod
    def put_message(self, queue_name: str, message: Union[str, bytes, Dict],
                   message_properties: Optional[Dict[str, Any]] = None) -> bool:
        """
        Put a message to a queue.

        @brief Send message to message queue.
        @param queue_name Name of the queue
        @param message Message content (string, bytes, or dictionary)
        @param message_properties Optional message properties
        @return True if message sent successfully, False otherwise
        @throws Exception If message sending fails
        """
        pass

    @abstractmethod
    def get_message(self, queue_name: str, timeout: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Get a message from a queue.

        @brief Receive message from message queue.
        @param queue_name Name of the queue
        @param timeout Timeout in seconds (None for default timeout)
        @return Dictionary containing message data and properties, or None if no message
        @throws Exception If message retrieval fails
        """
        pass

    @abstractmethod
    def browse_message(self, queue_name: str, message_id: Optional[bytes] = None) -> Optional[Dict[str, Any]]:
        """
        Browse a message from a queue without removing it.

        @brief Browse message without consuming it.
        @param queue_name Name of the queue
        @param message_id Specific message ID to browse (optional)
        @return Dictionary containing message data and properties, or None if no message
        @throws Exception If message browsing fails
        """
        pass

    @abstractmethod
    def get_queue_depth(self, queue_name: str) -> int:
        """
        Get the depth (number of messages) in a queue.

        @brief Get current queue depth.
        @param queue_name Name of the queue
        @return Number of messages in the queue, -1 if error
        @throws Exception If queue depth retrieval fails
        """
        pass

    @abstractmethod
    def purge_queue(self, queue_name: str) -> int:
        """
        Purge all messages from a queue.

        @brief Clear all messages from queue.
        @param queue_name Name of the queue
        @return Number of messages purged
        @throws Exception If queue purging fails
        """
        pass

    @abstractmethod
    def test_connection(self) -> bool:
        """
        Test messaging connection.

        @brief Test if messaging connection is working properly.
        @return True if connection is working, False otherwise
        """
        pass
