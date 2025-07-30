"""
Example 2: File Processing with GoAsyncIO
"""

import asyncio
import goasyncio
import os


async def process_files():
    """Process multiple files with high-performance I/O"""
    print("GoAsyncIO File Processing Example")
    print("=" * 40)
    
    # Create sample files for testing
    test_files = []
    for i in range(1, 4):
        filename = f"sample_file_{i}.txt"
        content = f"This is sample file {i}\\nProcessed by GoAsyncIO\\nHigh-performance file I/O!"
        
        with open(filename, "w") as f:
            f.write(content)
        test_files.append(filename)
        print(f"📝 Created {filename}")
    
    # Initialize GoAsyncIO client
    async with goasyncio.Client() as client:
        # Check server health
        if not await client.health_check():
            print("❌ GoAsyncIO server is not running!")
            return
        
        print("✅ GoAsyncIO server is healthy")
        print(f"\\nProcessing {len(test_files)} files...")
        
        # Submit file reading tasks
        tasks = []
        for i, filename in enumerate(test_files, 1):
            try:
                task_id = await client.submit_task(
                    task_type="read_file",
                    data={"path": filename}
                )
                tasks.append((i, filename, task_id))
                print(f"✅ File {i}: Task {task_id} submitted for {filename}")
            except Exception as e:
                print(f"❌ File {i}: Failed to submit - {e}")
        
        print(f"\\n🚀 Successfully submitted {len(tasks)} file processing tasks!")
        print("Files are being processed with Go's high-performance I/O.")
    
    # Cleanup test files
    print("\\n🧹 Cleaning up test files...")
    for filename in test_files:
        try:
            os.remove(filename)
            print(f"🗑️ Removed {filename}")
        except Exception as e:
            print(f"⚠️ Could not remove {filename}: {e}")


if __name__ == "__main__":
    asyncio.run(process_files())
