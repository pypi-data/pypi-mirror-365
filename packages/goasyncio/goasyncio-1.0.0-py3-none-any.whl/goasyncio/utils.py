"""
GoAsyncIO Utility Functions
"""

import asyncio
import time
from typing import Dict, Any, Optional
from .client import Client


async def http_get(url: str, **kwargs) -> str:
    """
    High-performance HTTP GET request
    
    Args:
        url: URL to fetch
        **kwargs: Additional client options
    
    Returns:
        str: Task ID
    """
    async with Client(**kwargs) as client:
        return await client.submit_task("http_get", {"url": url})


async def read_file(path: str, **kwargs) -> str:
    """
    High-performance file reading
    
    Args:
        path: File path to read
        **kwargs: Additional client options
    
    Returns:
        str: Task ID
    """
    async with Client(**kwargs) as client:
        return await client.submit_task("read_file", {"path": path})


async def health_check(**kwargs) -> bool:
    """
    Check GoAsyncIO server health
    
    Args:
        **kwargs: Additional client options
    
    Returns:
        bool: True if healthy
    """
    client = Client(**kwargs)
    try:
        return await client.health_check()
    finally:
        await client.close()


async def benchmark_performance(
    num_tasks: int = 100,
    task_type: str = "http_get",
    task_data: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Benchmark GoAsyncIO performance
    
    Args:
        num_tasks: Number of tasks to submit
        task_type: Type of task to benchmark
        task_data: Data for tasks
        **kwargs: Additional client options
    
    Returns:
        dict: Benchmark results
    """
    if task_data is None:
        task_data = {"url": "https://httpbin.org/json"}
    
    start_time = time.time()
    successful_tasks = 0
    
    async with Client(**kwargs) as client:
        # Submit tasks in batches to avoid overwhelming
        batch_size = 20
        for i in range(0, num_tasks, batch_size):
            batch_end = min(i + batch_size, num_tasks)
            
            for _ in range(i, batch_end):
                try:
                    task_id = await client.submit_task(task_type, task_data)
                    if task_id:
                        successful_tasks += 1
                except Exception:
                    pass
            
            # Small delay between batches
            await asyncio.sleep(0.01)
    
    end_time = time.time()
    duration = end_time - start_time
    rps = num_tasks / duration if duration > 0 else 0
    
    return {
        "total_tasks": num_tasks,
        "successful_tasks": successful_tasks,
        "duration": duration,
        "rps": rps,
        "success_rate": (successful_tasks / num_tasks) * 100 if num_tasks > 0 else 0
    }
