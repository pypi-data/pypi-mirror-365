"""
Test configuration for GoAsyncIO
"""

import pytest
import asyncio


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def goasyncio_client():
    """Fixture to provide a GoAsyncIO client for testing"""
    import goasyncio
    
    client = goasyncio.Client()
    await client.connect()
    yield client
    await client.close()


@pytest.fixture
def sample_urls():
    """Sample URLs for testing"""
    return [
        "https://httpbin.org/json",
        "https://httpbin.org/uuid",
        "https://httpbin.org/ip"
    ]
