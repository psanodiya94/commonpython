"""
MQ Manager for CommonPython Framework

Provides IBM MQ connectivity and operations using CLI interface with support for:
- Connection management
- Message sending and receiving
- Queue browsing
- Message properties
- Error handling and logging
"""

import json
import os
import subprocess
import tempfile
import time
from typing import Any, Dict, List, Optional, Union


class MQManager:
    """
    IBM MQ manager for the CommonPython framework using CLI interface.

    Provides connection management, message operations, and queue handling
    using IBM MQ command-line tools instead of SDK modules.
    """

    def __init__(self, config: Dict[str, Any], logger=None):
        """
        Initialize the MQ manager.

        @brief Initialize the MQ manager with configuration and logger.
        @param config MQ configuration dictionary
        @param logger Logger manager instance (optional)
        """
        self.config = config
        self.logger = logger
        self.connection_info = self._build_connection_info()
        self.connected = False

    def _build_connection_info(self) -> Dict[str, Any]:
        """
        Build MQ connection information from configuration.

        @brief Create connection information for MQ CLI commands.
        @return Dictionary containing connection parameters
        """
        return {
            "host": self.config.get("host", "localhost"),
            "port": self.config.get("port", 1414),
            "queue_manager": self.config.get("queue_manager", "QM1"),
            "channel": self.config.get("channel", "SYSTEM.DEF.SVRCONN"),
            "user": self.config.get("user", ""),
            "password": self.config.get("password", ""),
            "timeout": self.config.get("timeout", 30),
        }

    def _execute_mq_command(
        self, command: str, params: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Execute an MQ CLI command.

        @brief Execute MQ CLI command and return results.
        @param command MQ CLI command to execute
        @param params Optional parameters for the command
        @return Dictionary containing command results and metadata
        @throws Exception If command execution fails
        """
        try:
            # Prepare the full command
            full_command = ["runmqsc", self.connection_info["queue_manager"]]
            if params:
                full_command.extend(params)

            # Execute the command
            result = subprocess.run(
                full_command, capture_output=True, text=True, timeout=self.config.get("timeout", 30)
            )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
            }

        except subprocess.TimeoutExpired:
            if self.logger:
                self.logger.logger.error(f"MQ command timeout: {command}")
            raise Exception(f"MQ command timeout: {command}") from None
        except Exception as e:
            if self.logger:
                self.logger.logger.error(f"MQ command error: {str(e)}")
            raise Exception(f"MQ command error: {str(e)}") from e

    def connect(self) -> bool:
        """
        Establish connection to MQ queue manager.

        @brief Test connection to MQ queue manager using CLI.
        @return True if connection successful, False otherwise
        """
        try:
            # Test connection by querying queue manager
            result = self._execute_mq_command("display", ["qmgr"])

            if result["success"]:
                self.connected = True
                if self.logger:
                    self.logger.logger.info(
                        f"Successfully connected to MQ queue manager: {self.connection_info['queue_manager']}"
                    )
                return True
            else:
                if self.logger:
                    self.logger.logger.error(
                        f"Failed to connect to MQ queue manager: {result['stderr']}"
                    )
                return False

        except Exception as e:
            if self.logger:
                self.logger.logger.error(f"MQ connection error: {str(e)}")
            return False

    def disconnect(self) -> None:
        """
        Close the MQ connection.

        @brief Disconnect from MQ queue manager using CLI.
        """
        try:
            if self.connected:
                self.connected = False
                if self.logger:
                    self.logger.logger.info("MQ connection closed")
        except Exception as e:
            if self.logger:
                self.logger.logger.error(f"Error closing MQ connection: {str(e)}")

    def is_connected(self) -> bool:
        """
        Check if MQ connection is active.

        @brief Check if MQ connection is established.
        @return True if connected, False otherwise
        """
        return self.connected

    def put_message(
        self,
        queue_name: str,
        message: Union[str, bytes, Dict],
        message_properties: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Put a message to a queue.

        @brief Send message to MQ queue using CLI tools.
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
            # Convert message to string if needed
            if isinstance(message, dict):
                message_str = json.dumps(message)
            elif isinstance(message, bytes):
                message_str = message.decode("utf-8")
            else:
                message_str = str(message)

            # Create temporary file for message content
            with tempfile.NamedTemporaryFile(mode="w", suffix=".msg", delete=False) as f:
                f.write(message_str)
                temp_file = f.name

            # Use amqsput command to put message
            result = subprocess.run(
                ["amqsput", queue_name, self.connection_info["queue_manager"]],
                input=message_str,
                text=True,
                capture_output=True,
                timeout=self.config.get("timeout", 30),
            )

            # Clean up temporary file
            os.unlink(temp_file)

            if result.returncode == 0:
                duration = time.time() - start_time
                if self.logger:
                    self.logger.log_mq_operation(
                        operation="PUT",
                        queue=queue_name,
                        message_size=len(message_str.encode("utf-8")),
                        duration=duration,
                    )
                return True
            else:
                if self.logger:
                    self.logger.logger.error(
                        f"Error putting message to queue {queue_name}: {result.stderr}"
                    )
                return False

        except Exception as e:
            duration = time.time() - start_time
            if self.logger:
                self.logger.logger.error(f"Error putting message to queue {queue_name}: {str(e)}")
                self.logger.log_mq_operation(operation="PUT", queue=queue_name, duration=duration)
            return False

    def get_message(
        self, queue_name: str, timeout: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get a message from a queue.

        @brief Receive message from MQ queue using CLI tools.
        @param queue_name Name of the queue
        @param timeout Timeout in seconds (None for no timeout)
        @return Dictionary containing message data and properties, or None if no message
        @throws Exception If message retrieval fails
        """
        if not self.is_connected():
            raise Exception("MQ connection not established")

        start_time = time.time()

        try:
            # Use amqsget command to get message
            result = subprocess.run(
                ["amqsget", queue_name, self.connection_info["queue_manager"]],
                capture_output=True,
                text=True,
                timeout=timeout or self.config.get("timeout", 30),
            )

            if result.returncode == 0 and result.stdout.strip():
                # Parse message content
                message_str = result.stdout.strip()

                # Try to parse as JSON, fallback to string
                try:
                    message_data = json.loads(message_str)
                except json.JSONDecodeError:
                    message_data = message_str

                # Create message properties (simplified for CLI)
                message_properties = {
                    "message_id": f"cli_{int(time.time())}",
                    "correlation_id": "",
                    "reply_to_queue": "",
                    "reply_to_queue_manager": "",
                    "message_type": 8,  # MQMT_DATAGRAM
                    "format": "MQSTR",
                    "priority": 4,
                    "persistence": 0,
                    "expiry": -1,
                    "put_time": int(time.time()),
                    "put_date": int(time.time()),
                }

                duration = time.time() - start_time
                if self.logger:
                    self.logger.log_mq_operation(
                        operation="GET",
                        queue=queue_name,
                        message_id=message_properties["message_id"],
                        message_size=len(message_str.encode("utf-8")),
                        duration=duration,
                    )

                return {
                    "data": message_data,
                    "properties": message_properties,
                    "raw_bytes": message_str.encode("utf-8"),
                }
            else:
                # No message available
                return None

        except Exception as e:
            duration = time.time() - start_time
            if self.logger:
                self.logger.logger.error(f"Error getting message from queue {queue_name}: {str(e)}")
                self.logger.log_mq_operation(operation="GET", queue=queue_name, duration=duration)
            raise

    def browse_message(
        self, queue_name: str, message_id: Optional[bytes] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Browse a message from a queue without removing it.

        @brief Browse message from MQ queue using CLI tools (simplified implementation).
        @param queue_name Name of the queue
        @param message_id Specific message ID to browse (not supported in CLI mode)
        @return Dictionary containing message data and properties, or None if no message
        @throws Exception If message browsing fails
        """
        if not self.is_connected():
            raise Exception("MQ connection not established")

        start_time = time.time()

        try:
            # For browsing, we'll use a combination of get and put back
            # This is a simplified approach - in practice, you'd need more sophisticated handling
            message = self.get_message(queue_name)

            if message:
                # Put the message back to simulate browsing
                self.put_message(queue_name, message["data"], message["properties"])

                duration = time.time() - start_time
                if self.logger:
                    self.logger.log_mq_operation(
                        operation="BROWSE",
                        queue=queue_name,
                        message_id=message["properties"]["message_id"],
                        message_size=len(str(message["data"]).encode("utf-8")),
                        duration=duration,
                    )

                return message
            else:
                return None

        except Exception as e:
            duration = time.time() - start_time
            if self.logger:
                self.logger.logger.error(
                    f"Error browsing message from queue {queue_name}: {str(e)}"
                )
                self.logger.log_mq_operation(
                    operation="BROWSE", queue=queue_name, duration=duration
                )
            raise

    def get_queue_depth(self, queue_name: str) -> int:
        """
        Get the depth (number of messages) in a queue.

        @brief Get queue depth using MQ CLI commands.
        @param queue_name Name of the queue
        @return Number of messages in the queue
        @throws Exception If queue depth retrieval fails
        """
        if not self.is_connected():
            raise Exception("MQ connection not established")

        try:
            # Use runmqsc to get queue depth
            result = self._execute_mq_command("display", ["queue", queue_name, "curdepth"])

            if result["success"]:
                # Parse the output to extract depth
                lines = result["stdout"].split("\n")
                for line in lines:
                    if "CURDEPTH" in line:
                        # Extract the depth value
                        parts = line.split()
                        for i, part in enumerate(parts):
                            if part == "CURDEPTH" and i + 1 < len(parts):
                                try:
                                    return int(parts[i + 1])
                                except ValueError:
                                    pass
                return 0
            else:
                if self.logger:
                    self.logger.logger.error(
                        f"Error getting queue depth for {queue_name}: {result['stderr']}"
                    )
                return -1

        except Exception as e:
            if self.logger:
                self.logger.logger.error(f"Error getting queue depth for {queue_name}: {str(e)}")
            return -1

    def purge_queue(self, queue_name: str) -> int:
        """
        Purge all messages from a queue.

        @brief Purge queue using MQ CLI commands.
        @param queue_name Name of the queue
        @return Number of messages purged
        @throws Exception If queue purging fails
        """
        if not self.is_connected():
            raise Exception("MQ connection not established")

        start_time = time.time()

        try:
            # Get current depth before purging
            initial_depth = self.get_queue_depth(queue_name)

            # Use runmqsc to clear the queue
            result = self._execute_mq_command("clear", ["queue", queue_name])

            if result["success"]:
                duration = time.time() - start_time
                if self.logger:
                    self.logger.log_mq_operation(
                        operation="PURGE", queue=queue_name, duration=duration
                    )
                return max(0, initial_depth)
            else:
                if self.logger:
                    self.logger.logger.error(
                        f"Error purging queue {queue_name}: {result['stderr']}"
                    )
                raise Exception(f"Failed to purge queue: {result['stderr']}")

        except Exception as e:
            duration = time.time() - start_time
            if self.logger:
                self.logger.logger.error(f"Error purging queue {queue_name}: {str(e)}")
                self.logger.log_mq_operation(operation="PURGE", queue=queue_name, duration=duration)
            raise

    def test_connection(self) -> bool:
        """
        Test MQ connection.

        @brief Test MQ connection using CLI.
        @return True if connection is working, False otherwise
        """
        try:
            # Test connection by querying queue manager
            result = self._execute_mq_command("display", ["qmgr"])
            return result["success"]
        except Exception as e:
            if self.logger:
                self.logger.logger.error(f"MQ connection test failed: {str(e)}")
            return False
