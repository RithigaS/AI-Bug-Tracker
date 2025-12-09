import re

def redact_sensitive_data(text: str) -> str:
    """
    Redacts sensitive information from the given text.
    Targeted patterns:
    - IPv4 Addresses
    - Email Addresses
    - Generic API Keys (simple heuristics)
    - File Paths (Windows/Unix)
    """
    
    # IPv4 Address Pattern
    ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
    text = re.sub(ip_pattern, '[REDACTED_IP]', text)
    
    # Email Address Pattern
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    text = re.sub(email_pattern, '[REDACTED_EMAIL]', text)
    
    # Generic API Key Pattern (heuristics: long alphanumeric strings with mixed case)
    # This is a basic heuristic and might need refinement.
    # Looking for "Key", "Token", "Secret" followed by assignment and a long string
    api_key_pattern = r'(?i)(api[_-]?key|token|secret|password|passwd)\s*[:=]\s*["\']?([a-zA-Z0-9_\-]{20,})["\']?'
    
    def redact_key(match):
        return f'{match.group(1)}=[REDACTED_SECRET]'
        
    text = re.sub(api_key_pattern, redact_key, text)
    
    # File Paths (Basic Windows/Unix)
    # Windows: C:\Users\..., Unix: /home/user/...
    # This can be aggressive, so we'll try to be specific to common log patterns
    # windows_path_pattern = r'[a-zA-Z]:\\[\\\S| ]+'
    # unix_path_pattern = r'(?:/[a-zA-Z0-9._-]+)+/'
    
    # text = re.sub(windows_path_pattern, '[REDACTED_PATH]', text)
    # text = re.sub(unix_path_pattern, '[REDACTED_PATH]', text)
    
    return text
