import socket
import time

def test_connect_latency(ip, port=443, timeout=0.5):
    """
    Connects to the IP:port via TCP and measures time.
    Returns latency in milliseconds (float), or None if failed/timeout.
    """
    start_time = time.time()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((ip, port))
        end_time = time.time()
        # Connection successful
        latency = (end_time - start_time) * 1000.0
        return latency
    except (socket.timeout, socket.error, OSError):
        return None
    finally:
        try:
            s.close()
        except:
            pass
