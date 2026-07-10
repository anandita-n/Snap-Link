import re
import string
import secrets
from urllib.parse import urlparse

def is_valid_url(url: str) -> bool:
    """
    Validates if a URL is well-formed.
    Requires http or https scheme, a netloc (domain/host) containing at least a dot, 
    or host to be 'localhost'.
    """
    if not url:
        return False
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ('http', 'https'):
            return False
        if not parsed.netloc:
            return False
        
        # Remove port number from netloc to check host
        host = parsed.netloc.split(':')[0]
        if host == 'localhost':
            return True
            
        # Ensure hostname is valid: no leading/trailing dots, no double dots
        if host.startswith('.') or host.endswith('.') or '..' in host:
            return False
            
        # Ensure there is at least one dot and each segment is a valid domain part
        parts = host.split('.')
        if len(parts) < 2:
            return False
            
        for part in parts:
            if not part or not re.match(r'^[a-zA-Z0-9-]{1,63}$', part):
                return False
                
        return True
    except Exception:
        return False

def is_valid_alias(alias: str) -> bool:
    """
    Validates if a custom alias is alphanumeric or hyphen, and within 1-30 characters.
    """
    if not alias:
        return False
    return bool(re.match(r'^[a-zA-Z0-9-]{1,30}$', alias))

def generate_short_code(length: int = 6) -> str:
    """
    Generates a cryptographically secure random alphanumeric short code.
    """
    chars = string.ascii_letters + string.digits
    return "".join(secrets.choice(chars) for _ in range(length))
