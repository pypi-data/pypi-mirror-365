"""
Performance tests for GoAsyncIO
"""

import pytest
import asyncio
import time
import statistics
import goasyncio


@pytest.mark.performance
class TestGoAsyncIOPerformance:
    """Performance tests for GoAsyncIO"""
    
    @pytest.mark.asyncio
    async def test_benchmark_performance_function(self):
        """Test the benchmark_performance utility function"""
        try:
            # Run a small benchmark
            results = await goasyncio.benchmark_performance(
                num_tasks=5,
                task_type="http_get",
                task_data={"url": "https://httpbin.org/json"}
            )
            
            # Verify results structure
            assert "total_tasks" in results
            assert "successful_tasks" in results
            assert "duration" in results
            assert "rps" in results
            assert "success_rate" in results
            
            # Verify data types
            assert isinstance(results["total_tasks"], int)
            assert isinstance(results["successful_tasks"], int)
            assert isinstance(results["duration"], float)
            assert isinstance(results["rps"], float)
            assert isinstance(results["success_rate"], float)
            
            # Verify logical constraints
            assert results["total_tasks"] == 5
            assert results["successful_tasks"] <= results["total_tasks"]
            assert results["duration"] > 0
            assert 0 <= results["success_rate"] <= 100
            
            print(f"✅ Benchmark completed: {results['rps']:.1f} RPS")
            
        except goasyncio.ServerConnectionError:
            pytest.skip("GoAsyncIO server not available for performance testing")
    
    @pytest.mark.asyncio
    async def test_concurrent_task_submission(self):
        """Test concurrent task submission performance"""
        try:
            async with goasyncio.Client() as client:
                if not await client.health_check():
                    pytest.skip("GoAsyncIO server not available")
                
                # Test concurrent submissions
                num_concurrent = 10
                start_time = time.time()
                
                tasks = []
                for i in range(num_concurrent):
                    task = client.submit_task(
                        "http_get",
                        {"url": f"https://httpbin.org/json?id={i}"}
                    )
                    tasks.append(task)
                
                # Wait for all submissions to complete
                task_ids = await asyncio.gather(*tasks, return_exceptions=True)
                end_time = time.time()
                
                duration = end_time - start_time
                successful = sum(1 for task_id in task_ids if isinstance(task_id, str))
                
                assert successful > 0, "At least some tasks should succeed"
                assert duration < 5.0, "Concurrent submissions should be fast"
                
                rps = successful / duration
                print(f"✅ Concurrent submission rate: {rps:.1f} tasks/sec")
                
        except goasyncio.ServerConnectionError:
            pytest.skip("GoAsyncIO server not available")
    
    @pytest.mark.asyncio
    async def test_response_time_consistency(self):
        """Test that response times are consistent"""
        try:
            async with goasyncio.Client() as client:
                if not await client.health_check():
                    pytest.skip("GoAsyncIO server not available")
                
                response_times = []
                num_requests = 10
                
                for i in range(num_requests):
                    start_time = time.time()
                    await client.submit_task(
                        "http_get",
                        {"url": "https://httpbin.org/json"}
                    )
                    end_time = time.time()
                    response_times.append(end_time - start_time)
                    
                    # Small delay between requests
                    await asyncio.sleep(0.01)
                
                # Calculate statistics
                avg_time = statistics.mean(response_times)
                max_time = max(response_times)
                min_time = min(response_times)
                std_dev = statistics.stdev(response_times) if len(response_times) > 1 else 0
                
                # Assertions for performance consistency
                assert avg_time < 0.1, f"Average response time too high: {avg_time:.3f}s"
                assert max_time < 0.5, f"Maximum response time too high: {max_time:.3f}s"
                assert std_dev < 0.05, f"Response time variation too high: {std_dev:.3f}s"
                
                print(f"✅ Response time stats:")
                print(f"   Average: {avg_time:.3f}s")
                print(f"   Min: {min_time:.3f}s")
                print(f"   Max: {max_time:.3f}s")
                print(f"   Std Dev: {std_dev:.3f}s")
                
        except goasyncio.ServerConnectionError:
            pytest.skip("GoAsyncIO server not available")


@pytest.mark.benchmark
class TestGoAsyncIOBenchmarks:
    """Benchmark tests using pytest-benchmark if available"""
    
    def test_health_check_benchmark(self, benchmark):
        """Benchmark health check performance"""
        async def health_check_async():
            try:
                return await goasyncio.health_check()
            except:
                return False
        
        def run_health_check():
            return asyncio.run(health_check_async())
        
        # Benchmark the health check
        result = benchmark(run_health_check)
        print(f"Health check result: {result}")
    
    def test_client_creation_benchmark(self, benchmark):
        """Benchmark client creation and cleanup"""
        async def create_and_cleanup_client():
            client = goasyncio.Client()
            await client.connect()
            await client.close()
            return True
        
        def run_client_lifecycle():
            return asyncio.run(create_and_cleanup_client())
        
        # Benchmark client lifecycle
        result = benchmark(run_client_lifecycle)
        assert result is True


@pytest.mark.stress
class TestGoAsyncIOStress:
    """Stress tests for GoAsyncIO"""
    
    @pytest.mark.asyncio
    async def test_high_volume_task_submission(self):
        """Test high volume task submission"""
        try:
            async with goasyncio.Client() as client:
                if not await client.health_check():
                    pytest.skip("GoAsyncIO server not available")
                
                # Submit a high number of tasks
                num_tasks = 100
                batch_size = 20
                successful_tasks = 0
                start_time = time.time()
                
                for batch_start in range(0, num_tasks, batch_size):
                    batch_end = min(batch_start + batch_size, num_tasks)
                    batch_tasks = []
                    
                    # Submit batch
                    for i in range(batch_start, batch_end):
                        task = client.submit_task(
                            "http_get",
                            {"url": f"https://httpbin.org/json?batch={i}"}
                        )
                        batch_tasks.append(task)
                    
                    # Wait for batch completion
                    results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                    successful_tasks += sum(1 for r in results if isinstance(r, str))
                    
                    # Small delay between batches
                    await asyncio.sleep(0.05)
                
                end_time = time.time()
                duration = end_time - start_time
                rps = successful_tasks / duration
                
                # Assertions
                assert successful_tasks > num_tasks * 0.8, "At least 80% of tasks should succeed"
                assert rps > 50, f"RPS too low for stress test: {rps:.1f}"
                
                print(f"✅ Stress test completed:")
                print(f"   Tasks: {num_tasks}")
                print(f"   Successful: {successful_tasks}")
                print(f"   Duration: {duration:.3f}s")
                print(f"   RPS: {rps:.1f}")
                
        except goasyncio.ServerConnectionError:
            pytest.skip("GoAsyncIO server not available for stress testing")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "performance"])
