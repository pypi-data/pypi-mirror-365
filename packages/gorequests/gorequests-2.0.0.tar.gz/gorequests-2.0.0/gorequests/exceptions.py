"""GoRequests exceptions module."""

class GoRequestsError(Exception):
    """Base exception for GoRequests."""
    pass

class TimeoutError(GoRequestsError):
    """Timeout exception."""
    pass

class ConnectionError(GoRequestsError):
    """Connection error exception."""
    pass

class HTTPError(GoRequestsError):
    """HTTP error exception."""
    pass

class RequestException(GoRequestsError):
    """General request exception."""
    pass

class InvalidURL(GoRequestsError):
    """Invalid URL exception."""
    pass
