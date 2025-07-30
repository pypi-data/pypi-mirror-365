"""
GoAsyncIO Client - High-Performance Async Client
"""

import asyncio
import aiohttp
import json
import time
from typing import Dict, Any, Optional, Union


class GoAsyncIOError(Exception):
    """Base exception for GoAsyncIO"""
    pass


class ServerConnectionError(GoAsyncIOError):
    """Raised when cannot connect to GoAsyncIO server"""
    pass


class TaskSubmissionError(GoAsyncIOError):
    """Raised when task submission fails"""
    pass


class Client:
    """
    GoAsyncIO high-performance client for task submission
    
    Provides async interface to communicate with Go backend server
    for superior performance compared to standard asyncio.
    
    Example:
        async with GoAsyncIO.Client() as client:
            task_id = await client.submit_task(
                task_type="http_get",
                data={"url": "https://api.example.com"}
            )
    """
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 8765,
        timeout: float = 30.0,
        max_connections: int = 100,
        keepalive_timeout: float = 30.0
    ):
        """
        Initialize GoAsyncIO client
        
        Args:
            host: GoAsyncIO server host
            port: GoAsyncIO server port
            timeout: Request timeout in seconds
            max_connections: Maximum concurrent connections
            keepalive_timeout: Keep-alive timeout
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self.base_url = f"http://{host}:{port}"
        self.session: Optional[aiohttp.ClientSession] = None
        self._connector_kwargs = {
            "limit": max_connections,
            "keepalive_timeout": keepalive_timeout,
            "enable_cleanup_closed": True
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
    
    async def connect(self):
        """Establish connection to GoAsyncIO server"""
        if self.session is None:
            connector = aiohttp.TCPConnector(**self._connector_kwargs)
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout
            )
    
    async def close(self):
        """Close connection to GoAsyncIO server"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def health_check(self) -> bool:
        """
        Check if GoAsyncIO server is healthy
        
        Returns:
            bool: True if server is healthy, False otherwise
        """
        if not self.session:
            await self.connect()
        
        try:
            if self.session:
                async with self.session.get(f"{self.base_url}/health") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get("status") == "healthy"
            return False
        except Exception:
            return False
    
    async def submit_task(
        self,
        task_type: str,
        data: Dict[str, Any],
        priority: int = 0
    ) -> str:
        """
        Submit a task to GoAsyncIO server for high-performance processing
        
        Args:
            task_type: Type of task ("http_get", "read_file", etc.)
            data: Task data dictionary
            priority: Task priority (0 = normal, higher = higher priority)
        
        Returns:
            str: Task ID for tracking
            
        Raises:
            ServerConnectionError: If cannot connect to server
            TaskSubmissionError: If task submission fails
        """
        if not self.session:
            await self.connect()
        
        # Check server health first
        if not await self.health_check():
            raise ServerConnectionError("GoAsyncIO server is not available")
        
        payload = {
            "type": task_type,
            "data": data,
            "priority": priority
        }
        
        try:
            if self.session:
                async with self.session.post(
                    f"{self.base_url}/api/task",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        return str(result.get("task_id"))
                    else:
                        error_text = await resp.text()
                        raise TaskSubmissionError(f"Task submission failed: {error_text}")
            else:
                raise ServerConnectionError("No active session")
        except aiohttp.ClientError as e:
            raise ServerConnectionError(f"Failed to connect to server: {e}")
    
    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get status of a submitted task
        
        Args:
            task_id: Task ID returned from submit_task()
        
        Returns:
            dict: Task status information
        """
        if not self.session:
            await self.connect()
        
        try:
            if self.session:
                async with self.session.get(f"{self.base_url}/api/task/{task_id}") as resp:
                    if resp.status == 200:
                        return await resp.json()
                    elif resp.status == 404:
                        return {"status": "not_found", "error": "Task not found"}
                    else:
                        error_text = await resp.text()
                        return {"status": "error", "error": error_text}
            else:
                return {"status": "error", "error": "No active session"}
        except aiohttp.ClientError as e:
            return {"status": "error", "error": str(e)}
