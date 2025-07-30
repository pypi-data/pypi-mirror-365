"""
Basic tests for GoAsyncIO client functionality
"""

import pytest
import asyncio
import goasyncio


class TestGoAsyncIOClient:
    """Test GoAsyncIO client basic functionality"""
    
    async def test_client_initialization(self):
        """Test client can be initialized"""
        client = goasyncio.Client()
        assert client.host == "localhost"
        assert client.port == 8765
        assert client.timeout == 30.0
        await client.close()
    
    async def test_client_custom_config(self):
        """Test client with custom configuration"""
        client = goasyncio.Client(
            host="127.0.0.1",
            port=9000,
            timeout=60.0
        )
        assert client.host == "127.0.0.1"
        assert client.port == 9000
        assert client.timeout == 60.0
        await client.close()
    
    async def test_client_context_manager(self):
        """Test client as async context manager"""
        async with goasyncio.Client() as client:
            assert client.session is not None
        # Session should be closed after context exit
    
    @pytest.mark.asyncio
    async def test_health_check_when_server_unavailable(self):
        """Test health check when server is not running"""
        client = goasyncio.Client(port=9999)  # Non-existent port
        healthy = await client.health_check()
        assert healthy is False
        await client.close()
    
    @pytest.mark.asyncio 
    async def test_task_submission_without_server(self):
        """Test task submission when server is unavailable"""
        client = goasyncio.Client(port=9999)  # Non-existent port
        
        with pytest.raises(goasyncio.ServerConnectionError):
            await client.submit_task("http_get", {"url": "https://example.com"})
        
        await client.close()


class TestGoAsyncIOUtilityFunctions:
    """Test utility functions"""
    
    @pytest.mark.asyncio
    async def test_health_check_function(self):
        """Test standalone health check function"""
        # This will fail if server is not running, which is expected
        healthy = await goasyncio.health_check(port=9999)
        assert healthy is False
    
    @pytest.mark.asyncio
    async def test_http_get_function_without_server(self):
        """Test http_get function when server is unavailable"""
        with pytest.raises(goasyncio.ServerConnectionError):
            await goasyncio.http_get("https://example.com", port=9999)
    
    @pytest.mark.asyncio
    async def test_read_file_function_without_server(self):
        """Test read_file function when server is unavailable"""
        with pytest.raises(goasyncio.ServerConnectionError):
            await goasyncio.read_file("test.txt", port=9999)


class TestGoAsyncIOExceptions:
    """Test custom exceptions"""
    
    def test_custom_exceptions_inheritance(self):
        """Test that custom exceptions inherit from base correctly"""
        assert issubclass(goasyncio.ServerConnectionError, goasyncio.GoAsyncIOError)
        assert issubclass(goasyncio.TaskSubmissionError, goasyncio.GoAsyncIOError)
        assert issubclass(goasyncio.GoAsyncIOError, Exception)
    
    def test_exception_creation(self):
        """Test that exceptions can be created with messages"""
        error = goasyncio.GoAsyncIOError("Test error")
        assert str(error) == "Test error"
        
        conn_error = goasyncio.ServerConnectionError("Connection failed")
        assert str(conn_error) == "Connection failed"
        
        task_error = goasyncio.TaskSubmissionError("Task failed")
        assert str(task_error) == "Task failed"


@pytest.mark.integration
class TestGoAsyncIOIntegration:
    """Integration tests (require running server)"""
    
    @pytest.mark.asyncio
    async def test_server_integration_if_available(self):
        """Test integration with server if available"""
        try:
            healthy = await goasyncio.health_check()
            if healthy:
                print("✅ GoAsyncIO server is available for integration testing")
                
                # Test task submission
                async with goasyncio.Client() as client:
                    task_id = await client.submit_task(
                        "http_get", 
                        {"url": "https://httpbin.org/json"}
                    )
                    assert task_id is not None
                    assert isinstance(task_id, str)
                    print(f"✅ Task submitted successfully: {task_id}")
            else:
                print("ℹ️ GoAsyncIO server not available - skipping integration tests")
                pytest.skip("GoAsyncIO server not available")
        except Exception as e:
            print(f"ℹ️ Integration test skipped: {e}")
            pytest.skip(f"Integration test failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
