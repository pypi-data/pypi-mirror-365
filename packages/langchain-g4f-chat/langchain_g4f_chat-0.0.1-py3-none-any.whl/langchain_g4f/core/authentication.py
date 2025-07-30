"""Authentication types and utilities for G4F providers."""

from enum import Enum
from typing import Optional, Dict, Any

class AuthType(Enum):
    """Authentication types for G4F providers."""
    NONE = "none"
    API_KEY = "api_key" 
    COOKIES = "cookies"
    HAR_FILE = "har_file"
    NODRIVER = "nodriver"
    UNKNOWN = "unknown"

def check_provider_auth(provider_name: str) -> Dict[str, Any]:
    """Check authentication requirements for a provider."""
    try:
        import g4f
        provider = getattr(g4f.Provider, provider_name, None)
        
        if not provider:
            return {
                'auth_type': AuthType.UNKNOWN,
                'needs_auth': False,
                'details': 'Provider not found'
            }
        
        needs_auth = getattr(provider, 'needs_auth', False)
        
        if not needs_auth:
            return {
                'auth_type': AuthType.NONE,
                'needs_auth': False,
                'details': 'No authentication required'
            }
        
        # Determine auth type
        auth_type = AuthType.UNKNOWN
        details = []
        
        if hasattr(provider, 'api_key'):
            auth_type = AuthType.API_KEY
            details.append('Requires API key')
            
        if hasattr(provider, 'cookies'):
            auth_type = AuthType.COOKIES
            details.append('Requires cookies')
            
        if hasattr(provider, 'har_file'):
            auth_type = AuthType.HAR_FILE
            details.append('Requires HAR file')
            
        if 'nodriver' in provider_name.lower():
            auth_type = AuthType.NODRIVER
            details.append('Uses nodriver automation')
        
        return {
            'auth_type': auth_type,
            'needs_auth': needs_auth,
            'details': '; '.join(details) if details else 'Authentication required'
        }
        
    except Exception as e:
        return {
            'auth_type': AuthType.UNKNOWN,
            'needs_auth': False,
            'details': f'Error checking auth: {e}'
        }
