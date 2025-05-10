import random
import string
import time

# Base62 characters (0-9, a-z, A-Z)
BASE62 = string.digits + string.ascii_lowercase + string.ascii_uppercase

def generate_short_code(length=6):
    """Generate a random base62 code for shortened URLs"""
    return ''.join(random.choice(BASE62) for _ in range(length))

def is_valid_custom_code(code):
    """Check if a custom code is valid (alphanumeric and reasonable length)"""
    if not code or len(code) > 20:
        return False
    return all(c in BASE62 for c in code)

def generate_unique_id():
    """Generate a unique ID based on current timestamp and random string"""
    timestamp = int(time.time() * 1000)
    random_str = ''.join(random.choice(string.hexdigits) for _ in range(8))
    return f"{timestamp}-{random_str}"