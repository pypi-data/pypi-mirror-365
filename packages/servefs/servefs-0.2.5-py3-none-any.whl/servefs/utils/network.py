import socket
from typing import List


def get_local_addresses() -> List[str]:
    """Get all local network addresses"""
    addresses = []
    try:
        # Get hostname
        hostname = socket.gethostname()
        # Get all IP addresses
        for info in socket.getaddrinfo(hostname, None):
            ip = info[4][0]
            if isinstance(ip, str) and ':' not in ip:  # Filter out IPv6 for simplicity
                addresses.append(ip)
        
        # Also add localhost
        if '127.0.0.1' not in addresses:
            addresses.append('127.0.0.1')
            
        # Remove duplicates and sort
        addresses = sorted(list(set(addresses)))
    except Exception:
        # Fallback to localhost if anything fails
        addresses = ['127.0.0.1']
    
    return addresses
