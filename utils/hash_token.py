import hashlib
def hash_token(token: str) -> str:
    """Hash the API token for secure session identification."""
    return hashlib.sha256(token.encode()).hexdigest()