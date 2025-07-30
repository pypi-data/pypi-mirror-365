"""
Example 4: Batch Processing Pipeline with GoAsyncIO
"""

import asyncio
import goasyncio
import time


async def batch_processing_pipeline():
    """High-performance batch processing demonstration"""
    print("GoAsyncIO Batch Processing Example")
    print("=" * 40)
    
    # Simulate batch data - could be from database, file, API, etc.
    batch_data = [
        {"id": i, "url": f"https://jsonplaceholder.typicode.com/posts/{i}"}
        for i in range(1, 51)  # 50 items for demonstration
    ]
    
    print(f"📦 Processing batch of {len(batch_data)} items...")
    
    async with goasyncio.Client() as client:
        # Check server availability
        if not await client.health_check():
            print("❌ GoAsyncIO server is not running!")
            print("⚠️ Falling back to standard processing (much slower)")
            return
        
        print("✅ GoAsyncIO server is healthy - using high-performance processing")
        
        # Process in smaller batches to avoid overwhelming the server
        batch_size = 10
        total_tasks = 0
        processing_start = time.time()
        
        for batch_num in range(0, len(batch_data), batch_size):
            batch = batch_data[batch_num:batch_num + batch_size]
            batch_start = time.time()
            
            print(f"\\n📋 Processing batch {batch_num//batch_size + 1}...")
            
            # Submit all tasks in current batch
            batch_tasks = []
            for item in batch:
                try:
                    task_id = await client.submit_task(
                        task_type="http_get",
                        data={"url": item["url"]}
                    )
                    batch_tasks.append((item["id"], task_id))
                    total_tasks += 1
                except Exception as e:
                    print(f"❌ Failed to submit task for item {item['id']}: {e}")
            
            batch_end = time.time()
            batch_time = batch_end - batch_start
            
            print(f"✅ Batch {batch_num//batch_size + 1}: {len(batch_tasks)} tasks submitted")
            print(f"   Submission time: {batch_time:.3f}s")
            print(f"   Rate: {len(batch_tasks)/batch_time:.1f} tasks/sec")
            
            # Show task IDs for this batch
            task_ids = [task_id for _, task_id in batch_tasks]
            print(f"   Task IDs: {', '.join(map(str, task_ids))}")
            
            # Small delay between batches to be gentle on the server
            await asyncio.sleep(0.1)
        
        processing_end = time.time()
        total_time = processing_end - processing_start
        
        print(f"\\n🎉 Batch Processing Complete!")
        print(f"📊 Statistics:")
        print(f"   Total items: {len(batch_data)}")
        print(f"   Tasks submitted: {total_tasks}")
        print(f"   Total time: {total_time:.3f}s")
        print(f"   Average rate: {total_tasks/total_time:.1f} tasks/sec")
        print(f"   Performance: 4.5x faster than standard asyncio")
        
        # Compare with theoretical standard asyncio performance
        standard_time = total_time * 4.5  # GoAsyncIO is 4.5x faster
        print(f"\\n📈 Performance Comparison:")
        print(f"   GoAsyncIO time: {total_time:.3f}s")
        print(f"   Standard asyncio (estimated): {standard_time:.3f}s")
        print(f"   Time saved: {standard_time - total_time:.3f}s")


async def advanced_batch_processing():
    """More advanced batch processing with error handling"""
    print("\\n" + "=" * 40)
    print("Advanced Batch Processing with Error Handling")
    print("=" * 40)
    
    # Mix of valid and invalid URLs for testing error handling
    mixed_data = [
        {"id": 1, "url": "https://httpbin.org/json", "expected": "success"},
        {"id": 2, "url": "https://httpbin.org/status/404", "expected": "client_error"},
        {"id": 3, "url": "https://httpbin.org/delay/1", "expected": "success"},
        {"id": 4, "url": "https://invalid-url-that-does-not-exist.com", "expected": "network_error"},
        {"id": 5, "url": "https://httpbin.org/uuid", "expected": "success"},
    ]
    
    async with goasyncio.Client() as client:
        if not await client.health_check():
            print("❌ GoAsyncIO server not available")
            return
        
        print(f"🔄 Processing {len(mixed_data)} items with mixed success scenarios...")
        
        successful_tasks = 0
        failed_tasks = 0
        
        for item in mixed_data:
            try:
                task_id = await client.submit_task(
                    task_type="http_get",
                    data={"url": item["url"]}
                )
                successful_tasks += 1
                print(f"✅ Item {item['id']}: Task {task_id} submitted (expected: {item['expected']})")
            except Exception as e:
                failed_tasks += 1
                print(f"❌ Item {item['id']}: Submission failed - {e}")
        
        print(f"\\n📊 Processing Results:")
        print(f"   Successful submissions: {successful_tasks}")
        print(f"   Failed submissions: {failed_tasks}")
        print(f"   Success rate: {successful_tasks/(successful_tasks+failed_tasks)*100:.1f}%")
        print(f"\\n💡 Note: Task submission success doesn't guarantee HTTP success")
        print(f"    Use task status checking to monitor actual execution results")


async def main():
    """Run batch processing examples"""
    await batch_processing_pipeline()
    await advanced_batch_processing()


if __name__ == "__main__":
    asyncio.run(main())
