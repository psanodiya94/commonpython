"""
Messaging Management Module

Provides IBM MQ connectivity and operations using CLI interface with support
for connection management, message sending and receiving, queue browsing,
message properties, and error handling using only standard Python modules.

@brief Messaging functionality for CommonPython Framework
@author CommonPython Framework Team
@version 2.0.0
@since 1.0.0
"""

from .mq_manager import MQManager

__all__ = ["MQManager"]
