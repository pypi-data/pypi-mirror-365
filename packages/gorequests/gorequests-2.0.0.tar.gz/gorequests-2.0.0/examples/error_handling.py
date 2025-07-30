#!/usr/bin/env python3
"""
GoRequests Error Handling and Timeouts Example

Demonstrates comprehensive error handling, timeout management,
and robust request patterns.
"""

import gorequests
import time


def timeout_examples():
    """Timeout handling examples."""
    print("⏱️ Timeout Handling Examples")
    print("-" * 32)
    
    # Quick timeout (should succeed)
    try:
        response = gorequests.get('https://httpbin.org/get', timeout=10)
        print(f"Quick request status: {response.get('status_code', 'N/A')}")
        print("✅ Quick request succeeded")
    except Exception as e:
        print(f"Quick request failed: {e}")
    
    # Delayed request with adequate timeout
    try:
        response = gorequests.get('https://httpbin.org/delay/2', timeout=5)
        print(f"Delayed request status: {response.get('status_code', 'N/A')}")
        print("✅ Delayed request succeeded")
    except Exception as e:
        print(f"Delayed request failed: {e}")
    
    # Timeout test (might timeout)
    try:
        print("🔄 Testing timeout with very short timeout...")
        response = gorequests.get('https://httpbin.org/delay/3', timeout=1)
        print(f"Timeout test status: {response.get('status_code', 'N/A')}")
        print("✅ Timeout test completed (unexpectedly fast!)")
    except Exception as e:
        print(f"⏰ Timeout occurred as expected: {type(e).__name__}")
    
    print("✅ Timeout examples completed")


def error_status_handling():
    """HTTP error status handling."""
    print("\n🚨 HTTP Error Status Handling")
    print("-" * 35)
    
    # Test different status codes
    status_codes = [200, 404, 500, 301, 418]
    
    for status in status_codes:
        try:
            response = gorequests.get(f'https://httpbin.org/status/{status}')
            status_code = response.get('status_code', 'Unknown')
            
            if status_code == 200:
                print(f"✅ Status {status}: Success")
            elif 300 <= status_code < 400:
                print(f"↩️ Status {status}: Redirect")
            elif 400 <= status_code < 500:
                print(f"❌ Status {status}: Client Error")
            elif 500 <= status_code < 600:
                print(f"💥 Status {status}: Server Error")
            else:
                print(f"❓ Status {status}: Unknown")
                
        except Exception as e:
            print(f"🚫 Status {status}: Exception - {e}")
    
    print("✅ Status code examples completed")


def connection_error_handling():
    """Connection error handling."""
    print("\n🔌 Connection Error Handling")
    print("-" * 33)
    
    # Test invalid URL
    try:
        response = gorequests.get('https://nonexistent-domain-12345.com')
        print(f"Invalid domain status: {response.get('status_code', 'N/A')}")
    except Exception as e:
        print(f"🚫 Invalid domain error (expected): {type(e).__name__}")
    
    # Test invalid port
    try:
        response = gorequests.get('https://httpbin.org:99999')
        print(f"Invalid port status: {response.get('status_code', 'N/A')}")
    except Exception as e:
        print(f"🚫 Invalid port error (expected): {type(e).__name__}")
    
    print("✅ Connection error examples completed")


def retry_pattern():
    """Retry pattern implementation."""
    print("\n🔄 Retry Pattern Example")
    print("-" * 28)
    
    def make_request_with_retry(url, max_retries=3, delay=1):
        """Make request with retry logic."""
        for attempt in range(max_retries + 1):
            try:
                print(f"  Attempt {attempt + 1}/{max_retries + 1}")
                response = gorequests.get(url, timeout=3)
                print(f"  ✅ Success on attempt {attempt + 1}")
                return response
            except Exception as e:
                if attempt < max_retries:
                    print(f"  ⚠️ Attempt {attempt + 1} failed: {e}")
                    print(f"  ⏳ Waiting {delay}s before retry...")
                    time.sleep(delay)
                    delay *= 2  # Exponential backoff
                else:
                    print(f"  💥 All {max_retries + 1} attempts failed")
                    raise e
    
    # Test retry with unreliable endpoint
    try:
        # This might fail randomly, demonstrating retry logic
        response = make_request_with_retry('https://httpbin.org/status/200')
        print("🎉 Retry pattern succeeded")
    except Exception as e:
        print(f"🚫 Retry pattern failed: {e}")
    
    print("✅ Retry pattern example completed")


def graceful_degradation():
    """Graceful degradation example."""
    print("\n🛡️ Graceful Degradation")
    print("-" * 26)
    
    def fetch_data_with_fallback():
        """Fetch data with fallback options."""
        
        # Primary endpoint
        try:
            response = gorequests.get('https://httpbin.org/json', timeout=5)
            if response.get('status_code') == 200:
                print("✅ Primary endpoint succeeded")
                return response
        except Exception as e:
            print(f"⚠️ Primary endpoint failed: {e}")
        
        # Fallback endpoint
        try:
            response = gorequests.get('https://httpbin.org/get', timeout=5)
            if response.get('status_code') == 200:
                print("✅ Fallback endpoint succeeded")
                return response
        except Exception as e:
            print(f"⚠️ Fallback endpoint failed: {e}")
        
        # Last resort - return cached/default data
        print("📦 Using default/cached data")
        return {"status": "offline", "data": "cached_data"}
    
    result = fetch_data_with_fallback()
    print(f"Final result type: {type(result).__name__}")
    print("✅ Graceful degradation example completed")


def comprehensive_error_handling():
    """Comprehensive error handling example."""
    print("\n🛠️ Comprehensive Error Handling")
    print("-" * 38)
    
    def robust_request(url, **kwargs):
        """Make a robust request with comprehensive error handling."""
        try:
            response = gorequests.get(url, **kwargs)
            
            # Check status code
            status_code = response.get('status_code', 0)
            if 200 <= status_code < 300:
                print(f"✅ Request successful: {status_code}")
                return response
            elif 300 <= status_code < 400:
                print(f"↩️ Redirect response: {status_code}")
                return response
            elif 400 <= status_code < 500:
                print(f"❌ Client error: {status_code}")
                return None
            elif 500 <= status_code < 600:
                print(f"💥 Server error: {status_code}")
                return None
            else:
                print(f"❓ Unknown status: {status_code}")
                return None
                
        except Exception as e:
            error_type = type(e).__name__
            print(f"🚫 Request failed with {error_type}: {e}")
            return None
    
    # Test with various scenarios
    test_urls = [
        'https://httpbin.org/get',           # Should succeed
        'https://httpbin.org/status/404',    # Client error
        'https://httpbin.org/status/500',    # Server error
        'https://invalid-url-test.fake',     # Connection error
    ]
    
    for url in test_urls:
        print(f"\n🔍 Testing: {url}")
        result = robust_request(url, timeout=3)
        if result:
            print("  📊 Request returned data")
        else:
            print("  🚫 Request failed or returned no data")
    
    print("\n✅ Comprehensive error handling completed")


def main():
    """Run all error handling examples."""
    print("🚀 GoRequests Error Handling & Timeouts")
    print("=" * 45)
    
    timeout_examples()
    error_status_handling()
    connection_error_handling()
    retry_pattern()
    graceful_degradation()
    comprehensive_error_handling()
    
    print("\n🎉 All error handling examples completed!")
    print("\nError Handling Best Practices:")
    print("  ✓ Always set appropriate timeouts")
    print("  ✓ Handle different types of exceptions")
    print("  ✓ Implement retry logic for transient failures")
    print("  ✓ Use graceful degradation with fallbacks")
    print("  ✓ Check HTTP status codes")
    print("  ✓ Log errors for debugging")


if __name__ == "__main__":
    main()
