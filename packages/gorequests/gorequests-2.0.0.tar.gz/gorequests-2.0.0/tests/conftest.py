"""
Test configuration for GoRequests test suite.
"""

import pytest
import gorequests


@pytest.fixture
def gorequests_client():
    """Provide a fresh GoRequests client for each test."""
    return gorequests


@pytest.fixture
def test_url():
    """Provide a test URL for HTTP requests."""
    return "https://httpbin.org"


@pytest.fixture
def sample_json_data():
    """Provide sample JSON data for testing."""
    return {
        "name": "GoRequests",
        "version": "2.0.0",
        "features": ["fast", "compatible", "easy"],
        "test": True
    }


@pytest.fixture
def sample_headers():
    """Provide sample headers for testing."""
    return {
        "User-Agent": "GoRequests-Test/2.0.0",
        "Accept": "application/json",
        "X-Test-Header": "pytest"
    }


@pytest.fixture
def timeout_settings():
    """Provide timeout settings for tests."""
    return {
        "short": 1,
        "medium": 5,
        "long": 10
    }
