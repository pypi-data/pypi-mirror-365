# GoRequests Documentation

## Quick Start Guide

### Installation
```bash
pip install gorequests
```

### Basic Usage
```python
import gorequests as requests

# Simple GET request
response = requests.get('https://api.example.com/data')
print(response.json())

# POST with JSON
response = requests.post('https://api.example.com/users', 
                        json={'name': 'John', 'email': 'john@example.com'})
```

## API Reference

### HTTP Methods

#### gorequests.get(url, **kwargs)
Sends a GET request.

**Parameters:**
- `url` (str): URL for the request
- `params` (dict, optional): Query parameters
- `headers` (dict, optional): HTTP headers
- `timeout` (int, optional): Request timeout in seconds

**Returns:**
- dict: Response data with status_code and content

#### gorequests.post(url, **kwargs)
Sends a POST request.

**Parameters:**
- `url` (str): URL for the request
- `json` (dict, optional): JSON data to send
- `data` (dict, optional): Form data to send
- `files` (dict, optional): Files to upload
- `headers` (dict, optional): HTTP headers
- `timeout` (int, optional): Request timeout in seconds

**Returns:**
- dict: Response data with status_code and content

#### gorequests.put(url, **kwargs)
Sends a PUT request. Same parameters as POST.

#### gorequests.delete(url, **kwargs)
Sends a DELETE request. Same parameters as GET.

#### gorequests.patch(url, **kwargs)
Sends a PATCH request. Same parameters as POST.

#### gorequests.head(url, **kwargs)
Sends a HEAD request. Same parameters as GET.

#### gorequests.options(url, **kwargs)
Sends an OPTIONS request. Same parameters as GET.

### Response Object

GoRequests returns responses as dictionaries with the following structure:

```python
{
    "status_code": 200,
    "headers": {...},
    "content": "...",
    # Plus any additional response data
}
```

Common response attributes:
- `status_code`: HTTP status code
- `headers`: Response headers
- `content`: Response body
- Additional fields based on response type

### Error Handling

```python
try:
    response = gorequests.get('https://api.example.com', timeout=5)
    if response['status_code'] == 200:
        print("Success!")
    else:
        print(f"Error: {response['status_code']}")
except Exception as e:
    print(f"Request failed: {e}")
```

### Performance Features

#### Connection Reuse
For multiple requests to the same domain, consider using sessions:

```python
session = gorequests.Session()  # If available
for i in range(10):
    response = session.get(f'https://api.example.com/item/{i}')
```

#### Memory Monitoring
```python
stats = gorequests.get_memory_stats()  # If available
print(f"Memory usage: {stats['alloc']} bytes")
```

## Advanced Usage

### Custom Headers
```python
headers = {
    'User-Agent': 'MyApp/1.0',
    'Authorization': 'Bearer token123',
    'Accept': 'application/json'
}
response = gorequests.get('https://api.example.com', headers=headers)
```

### File Uploads
```python
files = {'file': open('document.pdf', 'rb')}
response = gorequests.post('https://api.example.com/upload', files=files)
```

### Form Data
```python
data = {'username': 'user', 'password': 'pass'}
response = gorequests.post('https://api.example.com/login', data=data)
```

### Query Parameters
```python
params = {'search': 'python', 'page': 1, 'limit': 10}
response = gorequests.get('https://api.example.com/search', params=params)
```

### Timeouts
```python
# 5 second timeout
response = gorequests.get('https://api.example.com', timeout=5)
```

## Migration from Requests

GoRequests is designed as a drop-in replacement for the `requests` library:

```python
# Before (using requests)
import requests
response = requests.get('https://api.example.com')
data = response.json()

# After (using gorequests)
import gorequests as requests
response = requests.get('https://api.example.com')
data = response  # Already parsed JSON
```

### Key Differences
1. **Response Format**: GoRequests returns parsed JSON directly as dict
2. **Performance**: 5-10x faster than standard requests
3. **Memory**: Lower memory usage with Go garbage collector
4. **Error Handling**: Similar exception patterns but may have slight differences

## Performance Optimization

### Best Practices
1. **Use appropriate timeouts** to avoid hanging requests
2. **Reuse connections** when making multiple requests
3. **Handle errors gracefully** with try-catch blocks
4. **Monitor memory usage** in long-running applications

### Benchmarking
```python
import time
import gorequests

start = time.time()
response = gorequests.get('https://api.example.com')
elapsed = time.time() - start
print(f"Request took {elapsed:.3f} seconds")
```

## Troubleshooting

### Common Issues

#### Import Errors
```python
# Make sure GoRequests is installed
pip install gorequests

# Check installation
import gorequests
print(gorequests.__version__)  # If available
```

#### Connection Errors
```python
try:
    response = gorequests.get('https://api.example.com', timeout=10)
except Exception as e:
    print(f"Connection failed: {e}")
    # Check internet connection, URL, firewall, etc.
```

#### Timeout Issues
```python
# Increase timeout for slow APIs
response = gorequests.get('https://slow-api.example.com', timeout=30)
```

### Debug Mode
Set environment variable for debugging:
```bash
export GOREQUESTS_DEBUG=1
```

## Examples

See the `examples/` directory for comprehensive usage examples:
- `basic_usage.py`: Basic HTTP requests
- `performance_benchmark.py`: Performance comparison
- `session_management.py`: Session usage
- `file_operations.py`: File upload/download
- `error_handling.py`: Error handling patterns

## Support

- **GitHub Issues**: [https://github.com/coffeecms/gorequests/issues](https://github.com/coffeecms/gorequests/issues)
- **Documentation**: [https://gorequests.readthedocs.io](https://gorequests.readthedocs.io)
- **PyPI**: [https://pypi.org/project/gorequests/](https://pypi.org/project/gorequests/)
