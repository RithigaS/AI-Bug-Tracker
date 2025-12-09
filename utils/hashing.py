import hashlib

def generate_log_hash(content: str) -> str:
    """
    Generates a SHA-256 hash for the given string content.
    Used for deduplication of logs.
    """
    return hashlib.sha256(content.encode('utf-8')).hexdigest()
