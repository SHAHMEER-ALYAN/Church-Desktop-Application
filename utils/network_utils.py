import socket

def is_internet_available():
    """Check if internet connection exists (Google DNS ping)."""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False
