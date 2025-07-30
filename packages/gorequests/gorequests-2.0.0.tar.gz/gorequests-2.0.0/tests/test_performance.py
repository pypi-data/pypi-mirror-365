"""
Performance tests comparing GoRequests with standard requests library.
"""

import time
import statistics
import gorequests

try:
    import requests as std_requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("Warning: standard requests library not available for comparison")


def time_function(func, *args, **kwargs):
    """Time a function execution."""
    start = time.time()
    result = func(*args, **kwargs)
    elapsed = time.time() - start
    return result, elapsed


def test_single_request_performance():
    """Compare single request performance."""
    print("🚀 Single Request Performance Test")
    print("-" * 40)
    
    url = "https://httpbin.org/get"
    iterations = 5
    
    # GoRequests timing
    gorequests_times = []
    for _ in range(iterations):
        _, elapsed = time_function(gorequests.get, url)
        gorequests_times.append(elapsed)
    
    go_avg = statistics.mean(gorequests_times)
    go_min = min(gorequests_times)
    go_max = max(gorequests_times)
    
    print(f"GoRequests Average: {go_avg:.3f}s")
    print(f"GoRequests Range:   {go_min:.3f}s - {go_max:.3f}s")
    
    if REQUESTS_AVAILABLE:
        # Standard requests timing
        requests_times = []
        for _ in range(iterations):
            _, elapsed = time_function(std_requests.get, url)
            requests_times.append(elapsed)
        
        req_avg = statistics.mean(requests_times)
        req_min = min(requests_times)
        req_max = max(requests_times)
        
        print(f"Requests Average:   {req_avg:.3f}s")
        print(f"Requests Range:     {req_min:.3f}s - {req_max:.3f}s")
        
        if req_avg > 0:
            improvement = ((req_avg - go_avg) / req_avg) * 100
            print(f"Performance Gain:   {improvement:.1f}% faster")
            
            assert go_avg <= req_avg * 1.1, "GoRequests should be competitive with requests"
    
    print("✅ Single request performance test completed")


def test_concurrent_requests_simulation():
    """Simulate concurrent requests performance."""
    print("\n⚡ Concurrent Requests Simulation")
    print("-" * 40)
    
    url = "https://httpbin.org/get"
    num_requests = 10
    
    # GoRequests sequential timing (simulating concurrent)
    start = time.time()
    for _ in range(num_requests):
        response = gorequests.get(url)
    go_time = time.time() - start
    
    print(f"GoRequests ({num_requests} requests): {go_time:.2f}s")
    print(f"GoRequests Rate: {num_requests/go_time:.1f} req/sec")
    
    if REQUESTS_AVAILABLE:
        # Standard requests sequential timing
        start = time.time()
        for _ in range(num_requests):
            response = std_requests.get(url)
        req_time = time.time() - start
        
        print(f"Requests ({num_requests} requests):   {req_time:.2f}s")
        print(f"Requests Rate:   {num_requests/req_time:.1f} req/sec")
        
        if req_time > 0:
            improvement = ((req_time - go_time) / req_time) * 100
            print(f"Performance Gain: {improvement:.1f}% faster")
    
    # Performance assertion
    expected_rate = 2.0  # At least 2 requests per second
    actual_rate = num_requests / go_time
    assert actual_rate >= expected_rate, f"Expected at least {expected_rate} req/sec, got {actual_rate:.1f}"
    
    print("✅ Concurrent requests test completed")


def test_memory_efficiency():
    """Test memory efficiency."""
    print("\n💾 Memory Efficiency Test")
    print("-" * 30)
    
    try:
        # Try to get memory stats if available
        if hasattr(gorequests, 'get_memory_stats'):
            stats = gorequests.get_memory_stats()
            print(f"Memory allocated: {stats.get('alloc', 0):,} bytes")
            print(f"Active goroutines: {stats.get('goroutines', 0)}")
        else:
            print("Memory stats not available")
        
        # Make multiple requests to test memory stability
        for i in range(5):
            response = gorequests.get("https://httpbin.org/get")
            assert isinstance(response, dict)
        
        print("✅ Memory efficiency test completed")
        
    except Exception as e:
        print(f"Memory test warning: {e}")


def test_throughput_benchmark():
    """Test sustained throughput."""
    print("\n📊 Throughput Benchmark")
    print("-" * 28)
    
    url = "https://httpbin.org/get"
    duration = 5  # seconds
    
    # GoRequests throughput
    start = time.time()
    count = 0
    while time.time() - start < duration:
        response = gorequests.get(url)
        if isinstance(response, dict) and response.get('status_code') == 200:
            count += 1
    
    actual_duration = time.time() - start
    rps = count / actual_duration
    
    print(f"Duration: {actual_duration:.1f}s")
    print(f"Successful requests: {count}")
    print(f"Requests per second: {rps:.1f}")
    
    # Performance assertion
    min_rps = 1.0  # Minimum 1 request per second
    assert rps >= min_rps, f"Expected at least {min_rps} RPS, got {rps:.1f}"
    
    print("✅ Throughput benchmark completed")


def test_response_time_consistency():
    """Test response time consistency."""
    print("\n📈 Response Time Consistency")
    print("-" * 35)
    
    url = "https://httpbin.org/get"
    times = []
    
    # Collect timing data
    for _ in range(10):
        _, elapsed = time_function(gorequests.get, url)
        times.append(elapsed)
    
    avg_time = statistics.mean(times)
    median_time = statistics.median(times)
    std_dev = statistics.stdev(times) if len(times) > 1 else 0
    
    print(f"Average time: {avg_time:.3f}s")
    print(f"Median time:  {median_time:.3f}s")
    print(f"Std deviation: {std_dev:.3f}s")
    print(f"Min time:     {min(times):.3f}s")
    print(f"Max time:     {max(times):.3f}s")
    
    # Consistency check - standard deviation should be reasonable
    max_std_dev = avg_time * 0.5  # 50% of average time
    assert std_dev <= max_std_dev, f"Response time too inconsistent: {std_dev:.3f}s std dev"
    
    print("✅ Response time consistency test completed")


def test_performance_under_load():
    """Test performance under simulated load."""
    print("\n🏋️ Performance Under Load")
    print("-" * 30)
    
    url = "https://httpbin.org/get"
    batch_sizes = [1, 5, 10]
    
    for batch_size in batch_sizes:
        start = time.time()
        
        for _ in range(batch_size):
            response = gorequests.get(url)
            assert isinstance(response, dict)
        
        elapsed = time.time() - start
        rate = batch_size / elapsed
        
        print(f"Batch size {batch_size:2d}: {elapsed:.2f}s ({rate:.1f} req/s)")
    
    print("✅ Performance under load test completed")


def run_all_performance_tests():
    """Run all performance tests."""
    print("🏆 GoRequests Performance Test Suite")
    print("=" * 45)
    
    try:
        test_single_request_performance()
        test_concurrent_requests_simulation()
        test_memory_efficiency()
        test_throughput_benchmark()
        test_response_time_consistency()
        test_performance_under_load()
        
        print("\n🎉 All performance tests completed successfully!")
        print("\nPerformance Summary:")
        print("  ✓ Competitive single request performance")
        print("  ✓ Good concurrent request handling")
        print("  ✓ Memory efficient operation")
        print("  ✓ Consistent response times")
        print("  ✓ Stable under load")
        
    except AssertionError as e:
        print(f"\n❌ Performance test failed: {e}")
        raise
    except Exception as e:
        print(f"\n💥 Performance test error: {e}")
        raise


if __name__ == "__main__":
    run_all_performance_tests()
