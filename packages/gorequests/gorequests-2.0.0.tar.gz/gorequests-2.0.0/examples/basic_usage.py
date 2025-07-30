#!/usr/bin/env python3
"""
GoRequests Basic Usage Example

This example demonstrates basic HTTP requests using GoRequests
as a drop-in replacement for the standard requests library.
"""

import gorequests as requests
import json


def main():
    print("🚀 GoRequests Basic Usage Example")
    print("=" * 50)
    
    # Example 1: Simple GET request
    print("\n1. Simple GET Request:")
    try:
        response = requests.get('https://httpbin.org/get')
        print(f"   Status Code: {response.status_code}")
        print(f"   Response Time: {response.elapsed}ms")
        data = response.json()
        print(f"   User Agent: {data['headers'].get('User-Agent', 'N/A')}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Example 2: GET with parameters
    print("\n2. GET Request with Parameters:")
    try:
        params = {'q': 'python', 'limit': 10}
        response = requests.get('https://httpbin.org/get', params=params)
        data = response.json()
        print(f"   Status Code: {response.status_code}")
        print(f"   Query Args: {data['args']}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Example 3: POST with JSON data
    print("\n3. POST Request with JSON:")
    try:
        payload = {
            'name': 'GoRequests',
            'version': '2.0.0',
            'features': ['fast', 'compatible', 'easy']
        }
        response = requests.post('https://httpbin.org/post', json=payload)
        data = response.json()
        print(f"   Status Code: {response.status_code}")
        print(f"   Echo Data: {data['json']}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Example 4: Custom headers
    print("\n4. Request with Custom Headers:")
    try:
        headers = {
            'User-Agent': 'GoRequests/2.0.0',
            'Accept': 'application/json',
            'X-Custom-Header': 'Test-Value'
        }
        response = requests.get('https://httpbin.org/headers', headers=headers)
        data = response.json()
        print(f"   Status Code: {response.status_code}")
        print(f"   Custom Header: {data['headers'].get('X-Custom-Header', 'Not found')}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Example 5: Timeout handling
    print("\n5. Request with Timeout:")
    try:
        response = requests.get('https://httpbin.org/delay/1', timeout=5)
        print(f"   Status Code: {response.status_code}")
        print(f"   Response received within timeout")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n✅ Basic usage examples completed!")


if __name__ == "__main__":
    main()
