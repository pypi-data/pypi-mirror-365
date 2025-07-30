#!/usr/bin/env python3
"""
GoRequests Session Management Example

Demonstrates advanced session usage for connection reuse,
cookie handling, and authentication.
"""

import gorequests


def session_basic_example():
    """Basic session usage example."""
    print("🔗 Basic Session Example")
    print("-" * 30)
    
    # Create a session
    session = gorequests.Session()
    
    # Session automatically handles cookies
    response = session.get('https://httpbin.org/cookies/set/session_id/abc123')
    print(f"Set cookie status: {response.get('status_code', 'N/A')}")
    
    # Subsequent requests include cookies
    response = session.get('https://httpbin.org/cookies')
    print(f"Cookie response: {response.get('status_code', 'N/A')}")
    
    print("✅ Session example completed")


def session_authentication_example():
    """Session with authentication example."""
    print("\n🔐 Session Authentication Example")
    print("-" * 40)
    
    session = gorequests.Session()
    
    # Set default headers for all requests in this session
    session.headers = {
        'User-Agent': 'GoRequests-Session/2.0',
        'Accept': 'application/json'
    }
    
    # Simulate login
    login_data = {
        'username': 'testuser',
        'password': 'testpass'
    }
    
    response = session.post('https://httpbin.org/post', json=login_data)
    print(f"Login status: {response.get('status_code', 'N/A')}")
    
    # Now make authenticated requests
    response = session.get('https://httpbin.org/headers')
    print(f"Authenticated request status: {response.get('status_code', 'N/A')}")
    
    print("✅ Authentication example completed")


def session_connection_reuse():
    """Demonstrate connection reuse benefits."""
    print("\n⚡ Connection Reuse Example")
    print("-" * 35)
    
    import time
    
    # Without session (new connection each time)
    start = time.time()
    for i in range(5):
        response = gorequests.get('https://httpbin.org/get')
    no_session_time = time.time() - start
    
    # With session (connection reuse)
    start = time.time()
    session = gorequests.Session()
    for i in range(5):
        response = session.get('https://httpbin.org/get')
    session_time = time.time() - start
    
    improvement = ((no_session_time - session_time) / no_session_time) * 100
    
    print(f"Without session: {no_session_time:.3f}s")
    print(f"With session:    {session_time:.3f}s")
    print(f"Improvement:     {improvement:.1f}% faster")
    
    print("✅ Connection reuse example completed")


def session_error_handling():
    """Session error handling example."""
    print("\n🛡️ Session Error Handling")
    print("-" * 30)
    
    session = gorequests.Session()
    
    try:
        # Valid request
        response = session.get('https://httpbin.org/status/200')
        print(f"Success status: {response.get('status_code', 'N/A')}")
        
        # Error status
        response = session.get('https://httpbin.org/status/404')
        print(f"Error status: {response.get('status_code', 'N/A')}")
        
        # Timeout example
        response = session.get('https://httpbin.org/delay/1', timeout=2)
        print(f"Timeout test status: {response.get('status_code', 'N/A')}")
        
    except Exception as e:
        print(f"Handled error: {e}")
    
    print("✅ Error handling example completed")


def main():
    """Run all session examples."""
    print("🚀 GoRequests Session Management Examples")
    print("=" * 50)
    
    session_basic_example()
    session_authentication_example()
    session_connection_reuse()
    session_error_handling()
    
    print("\n🎉 All session examples completed successfully!")
    print("\nKey Benefits of Sessions:")
    print("  ✓ Connection reuse for better performance")
    print("  ✓ Automatic cookie handling")
    print("  ✓ Persistent headers and authentication")
    print("  ✓ Lower overhead for multiple requests")


if __name__ == "__main__":
    main()
