# GoAsyncIO Quick Start Guide

Get started with GoAsyncIO in just a few minutes! This guide will walk you through installation, basic usage, and your first high-performance async application.

## 🚀 Installation

### Requirements

- Python 3.7 or higher (3.8+ recommended)
- pip (Python package installer)

### Install from PyPI

```bash
pip install goasyncio
```

### Install from Source

```bash
git clone https://github.com/coffeecms/goasyncio.git
cd goasyncio
pip install -e .
```

## 🏃‍♂️ Quick Start

### 1. Your First GoAsyncIO Program

Create a file called `hello_goasyncio.py`:

```python
import asyncio
import goasyncio

async def main():
    # Create a GoAsyncIO client
    async with goasyncio.Client() as client:
        # Submit a simple task
        result = await client.submit_task("hello", {"name": "World"})
        print(f"Result: {result}")

# Run the program
if __name__ == "__main__":
    asyncio.run(main())
```

Run it:

```bash
python hello_goasyncio.py
```

### 2. Multiple Concurrent Tasks

```python
import asyncio
import goasyncio

async def process_multiple_tasks():
    async with goasyncio.Client() as client:
        # Submit multiple tasks concurrently
        tasks = []
        for i in range(5):
            task = client.submit_task("process", {"id": i, "data": f"task_{i}"})
            tasks.append(task)
        
        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks)
        
        for i, result in enumerate(results):
            print(f"Task {i}: {result}")

asyncio.run(process_multiple_tasks())
```

### 3. File Operations

```python
import asyncio
import goasyncio

async def process_files():
    async with goasyncio.Client() as client:
        # Read multiple files concurrently
        files = ["file1.txt", "file2.txt", "file3.txt"]
        read_tasks = [
            client.read_file(filename) 
            for filename in files
        ]
        
        contents = await asyncio.gather(*read_tasks)
        
        for filename, content in zip(files, contents):
            print(f"{filename}: {len(content)} bytes")

asyncio.run(process_files())
```

## 🎯 Key Concepts

### Client Management

GoAsyncIO uses a client-server architecture:

```python
# Option 1: Context manager (recommended)
async with goasyncio.Client() as client:
    result = await client.submit_task("task_type", data)

# Option 2: Manual management
client = goasyncio.Client()
await client.connect()
try:
    result = await client.submit_task("task_type", data)
finally:
    await client.disconnect()
```

### Task Types

GoAsyncIO supports various task types:

- **`"compute"`** - CPU-intensive computations
- **`"network"`** - Network requests and API calls
- **`"file"`** - File I/O operations
- **`"custom"`** - Your custom task implementations

### Error Handling

```python
import asyncio
import goasyncio

async def handle_errors():
    async with goasyncio.Client() as client:
        try:
            result = await client.submit_task("risky_task", {"data": "test"})
            print(f"Success: {result}")
        except goasyncio.TaskError as e:
            print(f"Task failed: {e}")
        except goasyncio.ConnectionError as e:
            print(f"Connection issue: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

asyncio.run(handle_errors())
```

## 📊 Performance Example

Compare GoAsyncIO with standard asyncio:

```python
import asyncio
import time
import goasyncio

async def benchmark_comparison():
    # Test data
    tasks_count = 100
    
    # GoAsyncIO version
    start_time = time.time()
    async with goasyncio.Client() as client:
        tasks = [
            client.submit_task("compute", {"n": i}) 
            for i in range(tasks_count)
        ]
        goasyncio_results = await asyncio.gather(*tasks)
    goasyncio_time = time.time() - start_time
    
    # Standard asyncio version (for comparison)
    start_time = time.time()
    async def compute_task(n):
        await asyncio.sleep(0.001)  # Simulate work
        return n * n
    
    asyncio_tasks = [compute_task(i) for i in range(tasks_count)]
    asyncio_results = await asyncio.gather(*asyncio_tasks)
    asyncio_time = time.time() - start_time
    
    print(f"GoAsyncIO: {goasyncio_time:.3f}s")
    print(f"Asyncio: {asyncio_time:.3f}s")
    print(f"Speedup: {asyncio_time / goasyncio_time:.1f}x")

asyncio.run(benchmark_comparison())
```

## 🔧 Configuration

### Client Configuration

```python
import goasyncio

# Default configuration
client = goasyncio.Client()

# Custom configuration
client = goasyncio.Client(
    host="localhost",
    port=8080,
    timeout=30.0,
    max_connections=100,
    retry_attempts=3
)
```

### Environment Variables

You can also configure using environment variables:

```bash
export GOASYNCIO_HOST=localhost
export GOASYNCIO_PORT=8080
export GOASYNCIO_TIMEOUT=30
export GOASYNCIO_MAX_CONNECTIONS=100
```

## 🛠️ Utility Functions

GoAsyncIO provides helpful utility functions:

```python
import goasyncio

# Batch processing
async def process_batch():
    data = [{"id": i, "value": i*2} for i in range(100)]
    
    async with goasyncio.Client() as client:
        # Process in batches of 10
        results = await goasyncio.process_batch(
            client, 
            "process_item", 
            data, 
            batch_size=10
        )
        print(f"Processed {len(results)} items")

# Timing utilities
async def measure_performance():
    async with goasyncio.Client() as client:
        with goasyncio.timer() as t:
            result = await client.submit_task("slow_task", {})
        print(f"Task completed in {t.elapsed:.3f}s")
```

## 🎨 Integration Examples

### With FastAPI

```python
from fastapi import FastAPI
import goasyncio

app = FastAPI()
goasyncio_client = None

@app.on_event("startup")
async def startup():
    global goasyncio_client
    goasyncio_client = goasyncio.Client()
    await goasyncio_client.connect()

@app.on_event("shutdown")
async def shutdown():
    if goasyncio_client:
        await goasyncio_client.disconnect()

@app.post("/process")
async def process_data(data: dict):
    result = await goasyncio_client.submit_task("process", data)
    return {"result": result}
```

### With aiohttp

```python
from aiohttp import web
import goasyncio

async def init_app():
    app = web.Application()
    app['goasyncio_client'] = goasyncio.Client()
    await app['goasyncio_client'].connect()
    
    app.router.add_post('/process', handle_process)
    return app

async def handle_process(request):
    data = await request.json()
    client = request.app['goasyncio_client']
    result = await client.submit_task("process", data)
    return web.json_response({"result": result})
```

## 🔍 Debugging Tips

### Enable Debug Logging

```python
import logging
import goasyncio

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('goasyncio')
logger.setLevel(logging.DEBUG)

async with goasyncio.Client() as client:
    # Your code here - debug logs will be shown
    pass
```

### Performance Monitoring

```python
import goasyncio

async with goasyncio.Client() as client:
    # Enable performance monitoring
    client.enable_monitoring()
    
    # Your tasks here
    result = await client.submit_task("task", {})
    
    # Get performance stats
    stats = client.get_stats()
    print(f"Tasks completed: {stats['completed']}")
    print(f"Average latency: {stats['avg_latency']:.3f}s")
    print(f"Requests per second: {stats['rps']:.1f}")
```

## 📚 Next Steps

Now that you've learned the basics:

1. **Explore Examples**: Check out the [examples directory](../examples/) for more complex use cases
2. **Read API Documentation**: See the [API Reference](api_reference.md) for complete function documentation
3. **Performance Optimization**: Learn about [Performance Best Practices](performance.md)
4. **Join the Community**: Visit our [GitHub repository](https://github.com/coffeecms/goasyncio)

## ❓ Common Issues

### Connection Errors

```python
# Handle connection issues
try:
    async with goasyncio.Client() as client:
        # Your code here
        pass
except goasyncio.ConnectionError:
    print("Could not connect to GoAsyncIO server")
    print("Make sure the server is running on the correct host/port")
```

### Task Timeouts

```python
# Set custom timeout
async with goasyncio.Client(timeout=60.0) as client:
    # Long-running task
    result = await client.submit_task("long_task", {})
```

### Performance Issues

If you're not seeing expected performance gains:

1. Ensure the GoAsyncIO server is running
2. Check network latency between client and server
3. Verify task complexity justifies the overhead
4. Monitor resource usage (CPU, memory)

## 🎉 Congratulations!

You've completed the GoAsyncIO Quick Start Guide! You now know how to:

- Install and set up GoAsyncIO
- Create basic async applications
- Handle errors and configure the client
- Integrate with web frameworks
- Debug and monitor performance

Happy coding with GoAsyncIO! 🚀
