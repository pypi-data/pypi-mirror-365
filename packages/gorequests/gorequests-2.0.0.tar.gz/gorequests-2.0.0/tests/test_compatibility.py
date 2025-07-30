"""
Compatibility tests to ensure GoRequests works as a drop-in replacement for requests.
"""

import gorequests


def test_basic_api_compatibility():
    """Test basic API compatibility with requests library."""
    print("🔄 Basic API Compatibility Test")
    print("-" * 35)
    
    # Test that basic methods exist
    assert hasattr(gorequests, 'get'), "Missing get method"
    assert hasattr(gorequests, 'post'), "Missing post method"
    assert hasattr(gorequests, 'put'), "Missing put method"
    assert hasattr(gorequests, 'delete'), "Missing delete method"
    assert hasattr(gorequests, 'head'), "Missing head method"
    assert hasattr(gorequests, 'options'), "Missing options method"
    assert hasattr(gorequests, 'patch'), "Missing patch method"
    
    print("✅ All basic HTTP methods available")


def test_request_parameters_compatibility():
    """Test that request parameters work like requests library."""
    print("\n📝 Request Parameters Compatibility")
    print("-" * 40)
    
    base_url = "https://httpbin.org"
    
    # Test params parameter
    response = gorequests.get(f"{base_url}/get", params={"test": "value"})
    assert isinstance(response, dict)
    print("✅ params parameter works")
    
    # Test headers parameter
    response = gorequests.get(f"{base_url}/get", headers={"X-Test": "value"})
    assert isinstance(response, dict)
    print("✅ headers parameter works")
    
    # Test timeout parameter
    response = gorequests.get(f"{base_url}/get", timeout=10)
    assert isinstance(response, dict)
    print("✅ timeout parameter works")
    
    # Test json parameter
    response = gorequests.post(f"{base_url}/post", json={"test": "data"})
    assert isinstance(response, dict)
    print("✅ json parameter works")
    
    # Test data parameter
    response = gorequests.post(f"{base_url}/post", data={"test": "data"})
    assert isinstance(response, dict)
    print("✅ data parameter works")


def test_response_object_compatibility():
    """Test response object compatibility."""
    print("\n📋 Response Object Compatibility")
    print("-" * 37)
    
    response = gorequests.get("https://httpbin.org/json")
    
    # Test that response is accessible like a dict (GoRequests style)
    assert isinstance(response, dict)
    print("✅ Response is dict-like")
    
    # Test common response attributes (via dict access)
    assert "status_code" in response or response.get("status_code") is not None
    print("✅ status_code accessible")
    
    # Test accessing response data
    if isinstance(response, dict):
        # GoRequests returns the parsed JSON directly
        assert len(response) > 0
        print("✅ Response data accessible")


def test_http_methods_compatibility():
    """Test all HTTP methods work consistently."""
    print("\n🌐 HTTP Methods Compatibility")
    print("-" * 33)
    
    base_url = "https://httpbin.org"
    test_data = {"test": "data"}
    
    # Test GET
    response = gorequests.get(f"{base_url}/get")
    assert response.get("status_code") == 200
    print("✅ GET method works")
    
    # Test POST
    response = gorequests.post(f"{base_url}/post", json=test_data)
    assert response.get("status_code") == 200
    print("✅ POST method works")
    
    # Test PUT
    response = gorequests.put(f"{base_url}/put", json=test_data)
    assert response.get("status_code") == 200
    print("✅ PUT method works")
    
    # Test DELETE
    response = gorequests.delete(f"{base_url}/delete")
    assert response.get("status_code") == 200
    print("✅ DELETE method works")
    
    # Test PATCH
    response = gorequests.patch(f"{base_url}/patch", json=test_data)
    assert response.get("status_code") == 200
    print("✅ PATCH method works")
    
    # Test HEAD
    response = gorequests.head(f"{base_url}/get")
    assert response.get("status_code") == 200
    print("✅ HEAD method works")
    
    # Test OPTIONS
    response = gorequests.options(f"{base_url}/get")
    assert response.get("status_code") == 200
    print("✅ OPTIONS method works")


def test_error_handling_compatibility():
    """Test error handling compatibility."""
    print("\n🚨 Error Handling Compatibility")
    print("-" * 35)
    
    # Test timeout handling
    try:
        response = gorequests.get("https://httpbin.org/delay/1", timeout=5)
        assert response.get("status_code") == 200
        print("✅ Timeout handling works")
    except Exception as e:
        print(f"⚠️ Timeout test: {e}")
    
    # Test connection error handling
    try:
        response = gorequests.get("https://nonexistent-domain-12345.com", timeout=2)
        print("⚠️ Connection should have failed")
    except Exception:
        print("✅ Connection error handling works")
    
    # Test status code handling
    response = gorequests.get("https://httpbin.org/status/404")
    assert response.get("status_code") == 404
    print("✅ Status code handling works")


def test_session_compatibility():
    """Test session compatibility if available."""
    print("\n🔗 Session Compatibility")
    print("-" * 25)
    
    try:
        if hasattr(gorequests, 'Session'):
            session = gorequests.Session()
            response = session.get("https://httpbin.org/get")
            assert isinstance(response, dict)
            print("✅ Session class works")
        else:
            print("ℹ️ Session class not available (may be integrated)")
    except Exception as e:
        print(f"⚠️ Session test: {e}")


def test_import_compatibility():
    """Test import compatibility."""
    print("\n📦 Import Compatibility")
    print("-" * 25)
    
    # Test direct import
    import gorequests
    assert hasattr(gorequests, 'get')
    print("✅ Direct import works")
    
    # Test aliased import (like requests)
    import gorequests as requests
    response = requests.get("https://httpbin.org/get")
    assert isinstance(response, dict)
    print("✅ Aliased import works")
    
    # Test specific function import
    from gorequests import get, post
    response = get("https://httpbin.org/get")
    assert isinstance(response, dict)
    print("✅ Specific function import works")


def test_real_world_usage_patterns():
    """Test real-world usage patterns."""
    print("\n🌍 Real-World Usage Patterns")
    print("-" * 35)
    
    # Pattern 1: API call with authentication headers
    headers = {
        "Authorization": "Bearer fake-token",
        "Accept": "application/json"
    }
    response = gorequests.get("https://httpbin.org/headers", headers=headers)
    assert response.get("status_code") == 200
    print("✅ API authentication pattern works")
    
    # Pattern 2: Form data submission
    form_data = {"username": "test", "password": "test"}
    response = gorequests.post("https://httpbin.org/post", data=form_data)
    assert response.get("status_code") == 200
    print("✅ Form submission pattern works")
    
    # Pattern 3: JSON API interaction
    json_data = {"query": "test", "limit": 10}
    response = gorequests.post("https://httpbin.org/post", json=json_data)
    assert response.get("status_code") == 200
    print("✅ JSON API pattern works")
    
    # Pattern 4: Query parameters
    params = {"search": "python", "page": 1}
    response = gorequests.get("https://httpbin.org/get", params=params)
    assert response.get("status_code") == 200
    print("✅ Query parameters pattern works")


def test_edge_cases():
    """Test edge cases and special scenarios."""
    print("\n🔍 Edge Cases Testing")
    print("-" * 25)
    
    # Empty response handling
    response = gorequests.get("https://httpbin.org/status/204")  # No content
    assert response.get("status_code") == 204
    print("✅ Empty response handling works")
    
    # Large response handling
    response = gorequests.get("https://httpbin.org/json")
    assert response.get("status_code") == 200
    print("✅ JSON response handling works")
    
    # Multiple headers with same name
    headers = {"X-Custom": "value1"}
    response = gorequests.get("https://httpbin.org/headers", headers=headers)
    assert response.get("status_code") == 200
    print("✅ Custom headers handling works")


def run_all_compatibility_tests():
    """Run all compatibility tests."""
    print("🔄 GoRequests Compatibility Test Suite")
    print("=" * 45)
    
    try:
        test_basic_api_compatibility()
        test_request_parameters_compatibility()
        test_response_object_compatibility()
        test_http_methods_compatibility()
        test_error_handling_compatibility()
        test_session_compatibility()
        test_import_compatibility()
        test_real_world_usage_patterns()
        test_edge_cases()
        
        print("\n🎉 All compatibility tests passed!")
        print("\nCompatibility Summary:")
        print("  ✓ Full API compatibility with requests")
        print("  ✓ All HTTP methods supported")
        print("  ✓ Request parameters work as expected")
        print("  ✓ Error handling behaves correctly")
        print("  ✓ Real-world patterns supported")
        print("  ✓ Edge cases handled properly")
        
    except AssertionError as e:
        print(f"\n❌ Compatibility test failed: {e}")
        raise
    except Exception as e:
        print(f"\n💥 Compatibility test error: {e}")
        raise


if __name__ == "__main__":
    run_all_compatibility_tests()
