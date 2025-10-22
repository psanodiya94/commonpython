"""
MQ Library Adapter for CommonPython Framework

Adapter that uses the pymqi Python library for IBM MQ messaging operations.
Implements the IMessagingManager interface for library-based access.
"""

import json
import time
from typing import Any

from ..interfaces.messaging_interface import IMessagingManager

# Try to import pymqi library
try:
    import pymqi

    HAS_PYMQI = True
except ImportError:
    HAS_PYMQI = False


class MQLibraryAdapter(IMessagingManager):
    """
    Adapter for library-based MQ messaging operations using pymqi.

    Provides efficient, native IBM MQ connectivity using the pymqi Python library
    with support for connection pooling, message properties, and advanced
    messaging features.
    """

    def __init__(self, config: dict[str, Any], logger=None):
        """
        Initialize the MQ library adapter.

        @brief Initialize adapter with pymqi library.
        @param config Messaging configuration dictionary
        @param logger Logger manager instance (optional)
        @throws ImportError If pymqi library is not installed
        """
        if not HAS_PYMQI:
            raise ImportError(
                "pymqi library is not installed. " "Install it with: pip install pymqi"
            )

        self._config = config
        self._logger = logger
        self._qmgr = None
        self._connection_info = self._build_connection_info()

    def _build_connection_info(self) -> dict[str, Any]:
        """
        Build MQ connection information from configuration.

        @brief Create connection information for pymqi.
        @return Dictionary containing connection parameters
        """
        return {
            "host": self._config.get("host", "localhost"),
            "port": self._config.get("port", 1414),
            "queue_manager": self._config.get("queue_manager", "QM1"),
            "channel": self._config.get("channel", "SYSTEM.DEF.SVRCONN"),
            "user": self._config.get("user", ""),
            "password": self._config.get("password", ""),
            "timeout": self._config.get("timeout", 30),
        }

    def connect(self) -> bool:
        """
        Establish connection to MQ queue manager using pymqi library.

        @brief Connect to messaging server via pymqi library.
        @return True if connection successful, False otherwise
        """
        try:
            self._qmgr = pymqi.connect(
                self._connection_info["queue_manager"],
                self._connection_info["channel"],
                f"{self._connection_info['host']}({self._connection_info['port']})",
                self._connection_info["user"],
                self._connection_info["password"],
            )

            if self._logger:
                self._logger.logger.info(
                    f"Successfully connected to MQ queue manager: {self._connection_info['queue_manager']}"
                )
            return True

        except Exception as e:
            if self._logger:
                self._logger.logger.error(f"MQ connection error: {str(e)}")
            return False

    def disconnect(self) -> None:
        """
        Close the MQ connection.

        @brief Disconnect from messaging server via pymqi library.
        """
        try:
            if self._qmgr:
                self._qmgr.disconnect()
                self._qmgr = None

            if self._logger:
                self._logger.logger.info("MQ connection closed")

        except Exception as e:
            if self._logger:
                self._logger.logger.error(f"Error closing MQ connection: {str(e)}")

    def is_connected(self) -> bool:
        """
        Check if MQ connection is active.

        @brief Check pymqi connection status.
        @return True if connected, False otherwise
        """
        try:
            if self._qmgr and self._qmgr.is_connected:
                return True
        except Exception:
            pass
        return False

    def put_message(
        self,
        queue_name: str,
        message: str | bytes | dict,
        message_properties: dict[str, Any] | None = None,
    ) -> bool:
        """
        Put a message to a queue.

        @brief Send message to queue via pymqi with full property support.
        @param queue_name Name of the queue
        @param message Message content (string, bytes, or dictionary)
        @param message_properties Optional message properties
        @return True if message sent successfully, False otherwise
        @throws Exception If message sending fails
        """
        if not self.is_connected():
            raise Exception("MQ connection not established")

        start_time = time.time()

        try:
            # Open queue for output
            queue = pymqi.Queue(self._qmgr, queue_name)

            # Convert message to bytes if needed
            if isinstance(message, dict):
                message_bytes = json.dumps(message).encode("utf-8")
            elif isinstance(message, str):
                message_bytes = message.encode("utf-8")
            else:
                message_bytes = message

            # Create message descriptor
            md = pymqi.MD()
            if message_properties:
                if "correlation_id" in message_properties:
                    md.CorrelId = message_properties["correlation_id"]
                if "reply_to_queue" in message_properties:
                    md.ReplyToQ = message_properties["reply_to_queue"]
                if "message_type" in message_properties:
                    md.MsgType = message_properties["message_type"]
                if "priority" in message_properties:
                    md.Priority = message_properties["priority"]
                if "persistence" in message_properties:
                    md.Persistence = message_properties["persistence"]

            # Put message
            queue.put(message_bytes, md)
            queue.close()

            duration = time.time() - start_time
            if self._logger:
                self._logger.log_mq_operation(
                    operation="PUT",
                    queue=queue_name,
                    message_size=len(message_bytes),
                    duration=duration,
                )

            return True

        except Exception as e:
            duration = time.time() - start_time
            if self._logger:
                self._logger.logger.error(f"Error putting message to queue {queue_name}: {str(e)}")
                self._logger.log_mq_operation(operation="PUT", queue=queue_name, duration=duration)
            return False

    def get_message(self, queue_name: str, timeout: int | None = None) -> dict[str, Any] | None:
        """
        Get a message from a queue.

        @brief Receive message from queue via pymqi with full property support.
        @param queue_name Name of the queue
        @param timeout Timeout in seconds (None for default timeout)
        @return Dictionary containing message data and properties, or None if no message
        @throws Exception If message retrieval fails
        """
        if not self.is_connected():
            raise Exception("MQ connection not established")

        start_time = time.time()

        try:
            # Open queue for input
            queue = pymqi.Queue(self._qmgr, queue_name)

            # Create message descriptor and get options
            md = pymqi.MD()
            gmo = pymqi.GMO()
            gmo.Options = pymqi.CMQC.MQGMO_WAIT | pymqi.CMQC.MQGMO_FAIL_IF_QUIESCING
            gmo.WaitInterval = (timeout or self._connection_info["timeout"]) * 1000

            try:
                # Get message
                message_bytes = queue.get(None, md, gmo)
                queue.close()

                # Parse message content
                message_str = message_bytes.decode("utf-8")

                # Try to parse as JSON, fallback to string
                try:
                    message_data = json.loads(message_str)
                except json.JSONDecodeError:
                    message_data = message_str

                # Extract message properties
                message_properties = {
                    "message_id": md.MsgId.hex(),
                    "correlation_id": md.CorrelId.hex() if md.CorrelId else "",
                    "reply_to_queue": md.ReplyToQ.strip(),
                    "reply_to_queue_manager": md.ReplyToQMgr.strip(),
                    "message_type": md.MsgType,
                    "format": md.Format.strip(),
                    "priority": md.Priority,
                    "persistence": md.Persistence,
                    "expiry": md.Expiry,
                    "put_time": (
                        md.PutTime.decode("utf-8")
                        if hasattr(md.PutTime, "decode")
                        else str(md.PutTime)
                    ),
                    "put_date": (
                        md.PutDate.decode("utf-8")
                        if hasattr(md.PutDate, "decode")
                        else str(md.PutDate)
                    ),
                }

                duration = time.time() - start_time
                if self._logger:
                    self._logger.log_mq_operation(
                        operation="GET",
                        queue=queue_name,
                        message_id=message_properties["message_id"],
                        message_size=len(message_bytes),
                        duration=duration,
                    )

                return {
                    "data": message_data,
                    "properties": message_properties,
                    "raw_bytes": message_bytes,
                }

            except pymqi.MQMIError as e:
                queue.close()
                if (
                    e.comp == pymqi.CMQC.MQCC_FAILED
                    and e.reason == pymqi.CMQC.MQRC_NO_MSG_AVAILABLE
                ):
                    # No message available
                    return None
                else:
                    raise

        except Exception as e:
            duration = time.time() - start_time
            if self._logger:
                self._logger.logger.error(
                    f"Error getting message from queue {queue_name}: {str(e)}"
                )
                self._logger.log_mq_operation(operation="GET", queue=queue_name, duration=duration)
            raise

    def browse_message(
        self, queue_name: str, message_id: bytes | None = None
    ) -> dict[str, Any] | None:
        """
        Browse a message from a queue without removing it.

        @brief Browse message via pymqi without consuming it.
        @param queue_name Name of the queue
        @param message_id Specific message ID to browse (optional)
        @return Dictionary containing message data and properties, or None if no message
        @throws Exception If message browsing fails
        """
        if not self.is_connected():
            raise Exception("MQ connection not established")

        start_time = time.time()

        try:
            # Open queue for browse
            queue = pymqi.Queue(self._qmgr, queue_name, pymqi.CMQC.MQOO_BROWSE)

            # Create message descriptor and get options
            md = pymqi.MD()
            if message_id:
                md.MsgId = message_id

            gmo = pymqi.GMO()
            gmo.Options = pymqi.CMQC.MQGMO_BROWSE_FIRST | pymqi.CMQC.MQGMO_FAIL_IF_QUIESCING

            try:
                # Browse message
                message_bytes = queue.get(None, md, gmo)
                queue.close()

                # Parse message content
                message_str = message_bytes.decode("utf-8")

                # Try to parse as JSON, fallback to string
                try:
                    message_data = json.loads(message_str)
                except json.JSONDecodeError:
                    message_data = message_str

                # Extract message properties
                message_properties = {
                    "message_id": md.MsgId.hex(),
                    "correlation_id": md.CorrelId.hex() if md.CorrelId else "",
                    "reply_to_queue": md.ReplyToQ.strip(),
                    "message_type": md.MsgType,
                    "format": md.Format.strip(),
                    "priority": md.Priority,
                    "persistence": md.Persistence,
                }

                duration = time.time() - start_time
                if self._logger:
                    self._logger.log_mq_operation(
                        operation="BROWSE",
                        queue=queue_name,
                        message_id=message_properties["message_id"],
                        message_size=len(message_bytes),
                        duration=duration,
                    )

                return {
                    "data": message_data,
                    "properties": message_properties,
                    "raw_bytes": message_bytes,
                }

            except pymqi.MQMIError as e:
                queue.close()
                if (
                    e.comp == pymqi.CMQC.MQCC_FAILED
                    and e.reason == pymqi.CMQC.MQRC_NO_MSG_AVAILABLE
                ):
                    # No message available
                    return None
                else:
                    raise

        except Exception as e:
            duration = time.time() - start_time
            if self._logger:
                self._logger.logger.error(
                    f"Error browsing message from queue {queue_name}: {str(e)}"
                )
                self._logger.log_mq_operation(
                    operation="BROWSE", queue=queue_name, duration=duration
                )
            raise

    def get_queue_depth(self, queue_name: str) -> int:
        """
        Get the depth (number of messages) in a queue.

        @brief Get queue depth via pymqi.
        @param queue_name Name of the queue
        @return Number of messages in the queue, -1 if error
        """
        if not self.is_connected():
            raise Exception("MQ connection not established")

        try:
            # Open queue for inquire
            queue = pymqi.Queue(self._qmgr, queue_name, pymqi.CMQC.MQOO_INQUIRE)

            # Get current depth
            depth = queue.inquire(pymqi.CMQC.MQIA_CURRENT_Q_DEPTH)
            queue.close()

            return depth

        except Exception as e:
            if self._logger:
                self._logger.logger.error(f"Error getting queue depth for {queue_name}: {str(e)}")
            return -1

    def purge_queue(self, queue_name: str) -> int:
        """
        Purge all messages from a queue.

        @brief Purge queue via pymqi.
        @param queue_name Name of the queue
        @return Number of messages purged
        @throws Exception If queue purging fails
        """
        if not self.is_connected():
            raise Exception("MQ connection not established")

        start_time = time.time()

        try:
            # Open queue for input
            queue = pymqi.Queue(self._qmgr, queue_name)

            # Create get options for immediate return
            md = pymqi.MD()
            gmo = pymqi.GMO()
            gmo.Options = pymqi.CMQC.MQGMO_NO_WAIT | pymqi.CMQC.MQGMO_FAIL_IF_QUIESCING

            # Get and discard all messages
            purged_count = 0
            while True:
                try:
                    queue.get(None, md, gmo)
                    purged_count += 1
                except pymqi.MQMIError as e:
                    if e.reason == pymqi.CMQC.MQRC_NO_MSG_AVAILABLE:
                        break
                    else:
                        raise

            queue.close()

            duration = time.time() - start_time
            if self._logger:
                self._logger.log_mq_operation(
                    operation="PURGE", queue=queue_name, duration=duration
                )

            return purged_count

        except Exception as e:
            duration = time.time() - start_time
            if self._logger:
                self._logger.logger.error(f"Error purging queue {queue_name}: {str(e)}")
                self._logger.log_mq_operation(
                    operation="PURGE", queue=queue_name, duration=duration
                )
            raise

    def test_connection(self) -> bool:
        """
        Test MQ connection.

        @brief Test pymqi connection.
        @return True if connection is working, False otherwise
        """
        try:
            # Try to inquire queue manager
            if self._qmgr:
                pcf = pymqi.PCFExecute(self._qmgr)
                pcf.MQCMD_INQUIRE_Q_MGR()
                return True
            return False
        except Exception as e:
            if self._logger:
                self._logger.logger.error(f"MQ connection test failed: {str(e)}")
            return False
