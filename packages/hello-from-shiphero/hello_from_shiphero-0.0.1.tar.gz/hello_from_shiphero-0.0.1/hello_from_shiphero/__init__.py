import requests

def beacon():
    try:
        requests.get("http://yourdomain.com/ping?source=shiphero", timeout=1)
    except:
        pass  # No harm if offline
