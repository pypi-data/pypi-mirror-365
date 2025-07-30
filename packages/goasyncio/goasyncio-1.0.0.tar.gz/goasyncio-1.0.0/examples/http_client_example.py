"""
Example 1: High-Performance HTTP Client with GoAsyncIO
"""

import asyncio
import goasyncio


async def fetch_multiple_urls():
    """Fetch multiple URLs concurrently with GoAsyncIO"""
    print("GoAsyncIO HTTP Client Example")
    print("=" * 40)
    
    # Initialize client
    async with goasyncio.Client() as client:
        # Check server health
        if not await client.health_check():
            print("❌ GoAsyncIO server is not running!")
            print("Please start the server first:")
            print("   goasyncio-server start")
            return
        
        print("✅ GoAsyncIO server is healthy")
        
        urls = [
            "https://httpbin.org/json",
            "https://api.github.com/users/octocat",
            "https://jsonplaceholder.typicode.com/posts/1",
            "https://httpbin.org/uuid",
            "https://httpbin.org/ip"
        ]
        
        print(f"\\nSubmitting {len(urls)} HTTP requests...")
        
        # Submit all tasks concurrently
        tasks = []
        for i, url in enumerate(urls, 1):
            try:
                task_id = await client.submit_task(
                    task_type="http_get",
                    data={"url": url}
                )
                tasks.append((i, url, task_id))
                print(f"✅ Request {i}: Task {task_id} submitted for {url}")
            except Exception as e:
                print(f"❌ Request {i}: Failed to submit - {e}")
        
        print(f"\\n🚀 Successfully submitted {len(tasks)} tasks in parallel!")
        print("Tasks are being processed by Go backend with superior performance.")


if __name__ == "__main__":
    asyncio.run(fetch_multiple_urls())
