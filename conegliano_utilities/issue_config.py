"""
Issue Logger Configuration - Secure token and fallback options
"""

import os
import base64
from pathlib import Path
from typing import Optional


# OPTION 1: Hardcoded fallback token (encode it for basic obfuscation)
# To use: Replace 'YOUR_TOKEN_HERE' with your actual GitHub token
_FALLBACK_TOKEN = base64.b64encode(b"YOUR_TOKEN_HERE").decode()


def get_github_token() -> Optional[str]:
    """
    Get GitHub token from multiple sources with fallbacks.

    ~~~
    • Tries environment variable first (most secure)
    • Falls back to local config file
    • Uses hardcoded token as last resort
    • Returns None if no token found
    ~~~

    Returns type: token (Optional[str]) - GitHub personal access token or None
    """
    # Option 1: Environment variable (most secure)
    token = os.getenv('GITHUB_TOKEN')
    if token:
        return token

    # Option 2: Local config file (better than hardcoded)
    config_file = Path.home() / '.github_config' / 'token'
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                token = f.read().strip()
                if token and token != 'YOUR_TOKEN_HERE':
                    return token
        except Exception:
            pass

    # Option 3: Hardcoded fallback (least secure, but works)
    try:
        decoded_token = base64.b64decode(_FALLBACK_TOKEN).decode()
        if decoded_token != 'YOUR_TOKEN_HERE':
            return decoded_token
    except Exception:
        pass

    return None


def setup_token_config(token: str) -> bool:
    """
    Save GitHub token to local config file for future use.

    ~~~
    • Creates secure config directory in user home
    • Saves token to local file with restricted permissions
    • Returns success status
    • Provides better security than hardcoded tokens
    ~~~

    Args:
        token (str): GitHub personal access token to save

    Returns type: success (bool) - True if token was saved successfully
    """
    try:
        config_dir = Path.home() / '.github_config'
        config_dir.mkdir(exist_ok=True, mode=0o700)  # Restricted permissions

        config_file = config_dir / 'token'
        with open(config_file, 'w') as f:
            f.write(token)

        # Set file permissions to be readable only by owner
        config_file.chmod(0o600)
        return True

    except Exception:
        return False


def set_hardcoded_token(token: str) -> str:
    """
    Generate base64 encoded token for hardcoding (development only).

    ~~~
    • Encodes token in base64 for basic obfuscation
    • Returns encoded string for manual insertion
    • Not secure - only for development/testing
    • Should replace _FALLBACK_TOKEN value manually
    ~~~

    Args:
        token (str): GitHub personal access token to encode

    Returns type: encoded_token (str) - base64 encoded token string
    """
    return base64.b64encode(token.encode()).decode()


# Alternative repository configurations for different environments
REPO_CONFIGS = {
    'personal': {
        'owner': 'Norris36',
        'repo': 'jensbay_utilities',
        'public': True
    },
    'work': {
        'owner': 'your-work-org',
        'repo': 'internal-issues',
        'public': False
    },
    'backup': {
        'owner': 'Norris36',
        'repo': 'debug-issues',
        'public': True
    }
}