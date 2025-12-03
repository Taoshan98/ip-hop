class IPFetchError(Exception):
    """Raised when IP fetching fails from all sources."""
    pass

class ProviderError(Exception):
    """Raised when a DDNS provider update fails."""
    pass
