import time
import os
import base64

def generate_ulid():
    # Get the current timestamp in milliseconds
    timestamp = int(time.time() * 1000)
    # Generate 10 bytes of random data
    random_data = os.urandom(10)
    # Encode the timestamp and random data using Crockford's Base32 encoding
    ulid = base64.b32encode(timestamp.to_bytes(6, 'big') + random_data).decode('utf-8').replace('=', '')
    return ulid
