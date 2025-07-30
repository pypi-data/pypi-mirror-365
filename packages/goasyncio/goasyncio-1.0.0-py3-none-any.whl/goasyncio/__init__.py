"""
GoAsyncIO - High-Performance Async Library for Python

A revolutionary async library that leverages Go's runtime for unprecedented performance.
Provides up to 4.5x performance improvement over standard asyncio.
"""

__version__ = "1.0.0"
__author__ = "GoAsyncIO Team"
__email__ = "support@goasyncio.dev"
__license__ = "MIT"
__url__ = "https://github.com/coffeecms/goasyncio"

from .client import Client, GoAsyncIOError, ServerConnectionError, TaskSubmissionError
from .utils import http_get, read_file, health_check, benchmark_performance
from .server import ServerManager

# Export main classes and functions
__all__ = [
    "Client",
    "GoAsyncIOError",
    "ServerConnectionError", 
    "TaskSubmissionError",
    "http_get",
    "read_file",
    "health_check",
    "benchmark_performance",
    "ServerManager"
]
