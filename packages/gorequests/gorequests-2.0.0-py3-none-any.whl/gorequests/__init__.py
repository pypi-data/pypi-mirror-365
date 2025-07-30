#!/usr/bin/env python3
"""
GoRequests v2.0 - Fully Integrated Optimizations
Tích hợp tất cả helper functions và optimizations
"""
import ctypes
import json
import os
import sys
from typing import Dict, Any, Optional

__version__ = "2.0.0"

__version__ = "2.0.0"

class GoRequestsError(Exception):
    """Base exception for GoRequests"""
    pass

class Response:
    """Response object tương thích với requests.Response"""
    def __init__(self, data: dict):
        self._data = data
        self.status_code = data.get('status_code', 0)
        self.text = data.get('content', '')
        self.url = data.get('url', '')
        self.headers = data.get('headers', {})
        self.ok = 200 <= self.status_code < 300
    
    def json(self):
        """Parse response as JSON"""
        try:
            return json.loads(self.text)
        except:
            return None

class GoRequestsClient:
    """
    GoRequests Client - Tích hợp hoàn toàn tất cả optimizations
    
    ✅ Không cần setup functions nữa - auto setup
    ✅ Không cần helper functions nữa - đã tích hợp
    ✅ API đơn giản như requests library
    
    Usage:
        client = GoRequestsClient()  # Auto-setup everything!
        response = client.get('http://httpbin.org/get')
        print(response.status_code)
    """
    
    def __init__(self, dll_path: Optional[str] = None):
        """Initialize với automatic setup - không cần config gì thêm"""
        # Auto-detect DLL path
        if dll_path is None:
            current_dir = os.path.dirname(__file__)
            dll_path = os.path.join(current_dir, 'libgorequests.dll')
        
        if not os.path.exists(dll_path):
            raise GoRequestsError(f"Cannot find library at {dll_path}")
        
        # Load library và auto-setup
        self._lib = ctypes.CDLL(dll_path)
        self._setup_library_optimized()  # Tích hợp setup function
        self._session = self._create_session()
    
    def _setup_library_optimized(self):
        """
        🚀 Tích hợp setup_gorequests_lib function
        
        Thay vì người dùng phải:
            lib.GetMemoryStats.restype = ctypes.c_char_p
            lib.GetMemoryStats.argtypes = []
            lib.CreateSession.restype = ctypes.c_int
            lib.CreateSession.argtypes = []
            lib.GoSessionRequest.restype = ctypes.c_char_p
            lib.GoSessionRequest.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
        
        Giờ đây tự động được gọi trong __init__
        """
        # Core functions - automatically setup
        self._lib.GetMemoryStats.restype = ctypes.c_char_p
        self._lib.GetMemoryStats.argtypes = []
        
        self._lib.CreateSession.restype = ctypes.c_int
        self._lib.CreateSession.argtypes = []
        
        self._lib.GoSessionRequest.restype = ctypes.c_char_p
        self._lib.GoSessionRequest.argtypes = [
            ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p
        ]
        
        # Note: Không setup FreeMemory để tránh hanging
    
    def _create_session(self) -> int:
        """Create session automatically"""
        return self._lib.CreateSession()
    
    def memory_stats(self) -> dict:
        """
        🚀 Tích hợp get_memory_stats_simple function
        
        Thay vì:
            result = lib.GetMemoryStats()
            result_str = ctypes.cast(result, ctypes.c_char_p).value.decode('utf-8')
            stats = json.loads(result_str)
        
        Giờ đây:
            stats = client.memory_stats()
        """
        result = self._lib.GetMemoryStats()
        result_str = ctypes.cast(result, ctypes.c_char_p).value.decode('utf-8')
        return json.loads(result_str)
    
    def _request_optimized(self, method: str, url: str, **kwargs) -> Response:
        """
        🚀 Tích hợp make_request_simple function
        
        Thay vì phức tạp:
            result_ptr = lib.GoSessionRequest(session, b'GET', b'http://example.com', options)
            result_str = ctypes.cast(result_ptr, ctypes.c_char_p).value.decode('utf-8')
            result = json.loads(result_str)
        
        Giờ đây đơn giản: tự động xử lý trong _request_optimized()
        """
        # Prepare options với smart defaults
        options = {
            'timeout': kwargs.get('timeout', 10),
            'headers': kwargs.get('headers', {}),
            'params': kwargs.get('params', {}),
        }
        
        # Handle different data types intelligently
        if 'data' in kwargs:
            if isinstance(kwargs['data'], dict):
                options['data'] = json.dumps(kwargs['data'])
                options['headers'].setdefault('Content-Type', 'application/json')
            else:
                options['data'] = str(kwargs['data'])
        
        if 'json' in kwargs:
            options['data'] = json.dumps(kwargs['json'])
            options['headers']['Content-Type'] = 'application/json'
        
        # Auto-convert to proper formats
        options_json = json.dumps(options).encode('utf-8')
        method_bytes = method.encode()
        url_bytes = url.encode()
        
        # Make request - tất cả complexity được ẩn đi
        result_ptr = self._lib.GoSessionRequest(
            self._session,
            method_bytes,
            url_bytes,
            options_json
        )
        
        # Auto-parse response - không cần manual handling
        result_str = ctypes.cast(result_ptr, ctypes.c_char_p).value.decode('utf-8')
        result = json.loads(result_str)
        
        return Response(result)
    
    # HTTP methods - API hoàn toàn tương thích requests library
    def get(self, url: str, **kwargs) -> Response:
        """HTTP GET request - tương thích requests.get()"""
        return self._request_optimized('GET', url, **kwargs)
    
    def post(self, url: str, **kwargs) -> Response:
        """HTTP POST request - tương thích requests.post()"""
        return self._request_optimized('POST', url, **kwargs)
    
    def put(self, url: str, **kwargs) -> Response:
        """HTTP PUT request - tương thích requests.put()"""
        return self._request_optimized('PUT', url, **kwargs)
    
    def delete(self, url: str, **kwargs) -> Response:
        """HTTP DELETE request - tương thích requests.delete()"""
        return self._request_optimized('DELETE', url, **kwargs)
    
    def patch(self, url: str, **kwargs) -> Response:
        """HTTP PATCH request - tương thích requests.patch()"""
        return self._request_optimized('PATCH', url, **kwargs)
    
    def head(self, url: str, **kwargs) -> Response:
        """HTTP HEAD request - tương thích requests.head()"""
        return self._request_optimized('HEAD', url, **kwargs)
    
    def options(self, url: str, **kwargs) -> Response:
        """HTTP OPTIONS request - tương thích requests.options()"""
        return self._request_optimized('OPTIONS', url, **kwargs)

# Global client cho convenience - như requests library
_default_client = None

def _get_client():
    """Get hoặc create default client instance"""
    global _default_client
    if _default_client is None:
        _default_client = GoRequestsClient()
    return _default_client

# Global functions - API hoàn toàn tương thích requests library
def get(url: str, **kwargs) -> Response:
    """HTTP GET - drop-in replacement cho requests.get()"""
    return _get_client().get(url, **kwargs)

def post(url: str, **kwargs) -> Response:
    """HTTP POST - drop-in replacement cho requests.post()"""
    return _get_client().post(url, **kwargs)

def put(url: str, **kwargs) -> Response:
    """HTTP PUT - drop-in replacement cho requests.put()"""
    return _get_client().put(url, **kwargs)

def delete(url: str, **kwargs) -> Response:
    """HTTP DELETE - drop-in replacement cho requests.delete()"""
    return _get_client().delete(url, **kwargs)

def patch(url: str, **kwargs) -> Response:
    """HTTP PATCH - drop-in replacement cho requests.patch()"""
    return _get_client().patch(url, **kwargs)

def head(url: str, **kwargs) -> Response:
    """HTTP HEAD - drop-in replacement cho requests.head()"""
    return _get_client().head(url, **kwargs)

def options(url: str, **kwargs) -> Response:
    """HTTP OPTIONS - drop-in replacement cho requests.options()"""
    return _get_client().options(url, **kwargs)

def get_memory_stats() -> dict:
    """
    🚀 Tích hợp memory stats function - global access
    
    Thay vì setup library và call functions manually,
    giờ đây chỉ cần: stats = get_memory_stats()
    """
    try:
        return _get_client().memory_stats()
    except Exception as e:
        return {'error': str(e)}

# Compatibility aliases
Session = GoRequestsClient  # Alias for compatibility

# Demo và validation
if __name__ == "__main__":
    print("🚀 GoRequests v2.0 - Fully Integrated & Optimized")
    print("=" * 60)
    
    try:
        print("\n📦 Demo 1: Zero-config usage")
        print("   Code: import gorequests; response = gorequests.get('...')")
        
        # Sử dụng như requests library - zero configuration!
        response = get('http://httpbin.org/get', 
                      params={'integrated': 'true'},
                      headers={'User-Agent': 'GoRequests v2.0'})
        print(f"   ✅ Status: {response.status_code}")
        print(f"   ✅ URL: {response.url}")
        
        print("\n📦 Demo 2: Client-based usage")
        print("   Code: client = GoRequestsClient(); response = client.post(...)")
        
        # Client usage với auto-setup
        client = GoRequestsClient()
        post_response = client.post('http://httpbin.org/post',
                                   json={'message': 'Fully integrated!'},
                                   timeout=5)
        print(f"   ✅ POST Status: {post_response.status_code}")
        
        print("\n📦 Demo 3: Memory stats integrated")
        print("   Code: stats = get_memory_stats()")
        
        # Memory stats - no manual setup needed
        stats = get_memory_stats()
        print(f"   ✅ Memory: {stats['alloc']:,} bytes")
        print(f"   ✅ Sessions: {stats['sessions']}")
        
        print("\n📦 Demo 4: Multiple requests")
        import time
        start_time = time.time()
        for i in range(3):
            resp = get('http://httpbin.org/get', timeout=3)
            print(f"   Request {i+1}: Status {resp.status_code}")
        elapsed = time.time() - start_time
        print(f"   ✅ 3 requests: {elapsed:.2f}s")
        
        print("\n" + "=" * 60)
        print("🎉 FULL INTEGRATION SUCCESS!")
        print("✅ Zero configuration needed")
        print("✅ Drop-in replacement for requests")
        print("✅ All optimizations integrated")
        print("✅ No helper functions needed")
        print("✅ Auto-setup everything")
        print("✅ High performance with Go/FastHTTP backend")
        
        print("\n💡 MIGRATION FROM REQUESTS:")
        print("OLD:")
        print("   import requests")
        print("   response = requests.get('https://api.example.com')")
        print()
        print("NEW:")
        print("   import gorequests as requests  # Drop-in replacement!")
        print("   response = requests.get('https://api.example.com')")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
