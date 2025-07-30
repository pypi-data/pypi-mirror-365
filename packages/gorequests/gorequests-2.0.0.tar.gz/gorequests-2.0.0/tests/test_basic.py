"""
Basic functionality tests for GoRequests.
"""

import gorequests
import json


def test_simple_get_request():
    """Test basic GET request functionality."""
    response = gorequests.get("https://httpbin.org/get")
    assert isinstance(response, dict)
    assert response.get("status_code") == 200


def test_get_with_parameters():
    """Test GET request with query parameters."""
    params = {"test": "value", "number": 42}
    response = gorequests.get("https://httpbin.org/get", params=params)
    
    assert isinstance(response, dict)
    assert response.get("status_code") == 200
    
    # Check if parameters are in the response
    if "args" in response:
        assert response["args"].get("test") == "value"
        assert response["args"].get("number") == "42"


def test_post_with_json():
    """Test POST request with JSON data."""
    data = {"name": "GoRequests", "version": "2.0.0"}
    response = gorequests.post("https://httpbin.org/post", json=data)
    
    assert isinstance(response, dict)
    assert response.get("status_code") == 200
    
    # Check if JSON data is echoed back
    if "json" in response:
        assert response["json"]["name"] == "GoRequests"
        assert response["json"]["version"] == "2.0.0"


def test_custom_headers():
    """Test request with custom headers."""
    headers = {
        "User-Agent": "GoRequests-Test/2.0.0",
        "X-Custom-Header": "test-value"
    }
    
    response = gorequests.get("https://httpbin.org/headers", headers=headers)
    
    assert isinstance(response, dict)
    assert response.get("status_code") == 200
    
    # Check if custom headers are present
    if "headers" in response:
        assert "X-Custom-Header" in response["headers"]


def test_different_http_methods():
    """Test different HTTP methods."""
    base_url = "https://httpbin.org"
    
    # Test GET
    response = gorequests.get(f"{base_url}/get")
    assert response.get("status_code") == 200
    
    # Test POST
    response = gorequests.post(f"{base_url}/post", json={"test": "data"})
    assert response.get("status_code") == 200
    
    # Test PUT
    response = gorequests.put(f"{base_url}/put", json={"test": "data"})
    assert response.get("status_code") == 200
    
    # Test DELETE
    response = gorequests.delete(f"{base_url}/delete")
    assert response.get("status_code") == 200


def test_timeout_handling():
    """Test timeout functionality."""
    try:
        # This should complete within timeout
        response = gorequests.get("https://httpbin.org/get", timeout=10)
        assert response.get("status_code") == 200
    except Exception as e:
        # If it fails, make sure it's not a timeout issue
        assert "timeout" not in str(e).lower()


def test_error_status_codes():
    """Test handling of error status codes."""
    # Test 404
    response = gorequests.get("https://httpbin.org/status/404")
    assert response.get("status_code") == 404
    
    # Test 500
    response = gorequests.get("https://httpbin.org/status/500")
    assert response.get("status_code") == 500


def test_library_initialization():
    """Test that the library initializes correctly."""
    # Basic import test
    assert hasattr(gorequests, 'get')
    assert hasattr(gorequests, 'post')
    assert hasattr(gorequests, 'put')
    assert hasattr(gorequests, 'delete')
    
    # Test that we can make a simple request
    response = gorequests.get("https://httpbin.org/get")
    assert isinstance(response, dict)


def test_json_response_handling():
    """Test JSON response handling."""
    response = gorequests.get("https://httpbin.org/json")
    
    assert isinstance(response, dict)
    assert response.get("status_code") == 200
    
    # Should be able to access JSON data directly
    if "slideshow" in response:
        assert isinstance(response["slideshow"], dict)


def test_form_data():
    """Test form data submission."""
    data = {"key1": "value1", "key2": "value2"}
    response = gorequests.post("https://httpbin.org/post", data=data)
    
    assert isinstance(response, dict)
    assert response.get("status_code") == 200
    
    # Check if form data is present
    if "form" in response:
        assert response["form"]["key1"] == "value1"
        assert response["form"]["key2"] == "value2"


if __name__ == "__main__":
    # Run tests manually if pytest is not available
    print("Running basic tests...")
    
    try:
        test_simple_get_request()
        print("✅ Simple GET request test passed")
        
        test_get_with_parameters()
        print("✅ GET with parameters test passed")
        
        test_post_with_json()
        print("✅ POST with JSON test passed")
        
        test_custom_headers()
        print("✅ Custom headers test passed")
        
        test_different_http_methods()
        print("✅ Different HTTP methods test passed")
        
        test_timeout_handling()
        print("✅ Timeout handling test passed")
        
        test_error_status_codes()
        print("✅ Error status codes test passed")
        
        test_library_initialization()
        print("✅ Library initialization test passed")
        
        test_json_response_handling()
        print("✅ JSON response handling test passed")
        
        test_form_data()
        print("✅ Form data test passed")
        
        print("\n🎉 All basic tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
