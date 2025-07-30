"""Provider discovery and management for G4F."""

from typing import Dict, List, Any, Optional

try:
    import g4f
except ImportError as e:
    raise ImportError(
        "Could not import g4f python package. "
        "Please install it with `pip install g4f`."
    ) from e

class G4FProviderManager:
    """Manager for G4F providers and models."""
    
    def __init__(self):
        self._providers_cache = None
        self._working_providers_cache = None
    
    def get_all_providers(self) -> Dict[str, Any]:
        """Get all available providers with error handling."""
        if self._providers_cache is not None:
            return self._providers_cache
            
        providers = {}
        
        # Known working providers (manually curated to avoid ABCMeta errors)
        known_working = [
            'Free2GPT', 'DuckDuckGo', 'PollinationsAI', 'Bing', 
            'You', 'Blackbox', 'OpenaiChat', 'Copilot'
        ]
        
        for provider_name in known_working:
            try:
                provider = getattr(g4f.Provider, provider_name, None)
                if provider and hasattr(provider, '__name__'):
                    providers[provider_name] = {
                        'name': provider_name,
                        'class': provider,
                        'working': True,
                        'supports_chat': True,
                        'supports_image': provider_name in ['PollinationsAI', 'Bing'],
                        'needs_auth': provider_name in ['Bing', 'OpenaiChat', 'Copilot']
                    }
            except Exception:
                # Skip providers that cause errors
                continue
        
        self._providers_cache = providers
        return providers
    
    def get_all_models(self) -> List[str]:
        """Get available models."""
        models = [
            'gpt-3.5-turbo', 'gpt-4', 'gpt-4-turbo', 'claude-3',
            'gemini-pro', 'llama-2-7b', 'mistral-7b', 'flux'
        ]
        return models
    
    def categorize_providers_by_auth(self) -> Dict[str, List[str]]:
        """Categorize providers by authentication requirements."""
        return {
            'no_auth': ['Free2GPT', 'DuckDuckGo', 'PollinationsAI'],
            'cookies': ['Bing', 'OpenaiChat'],
            'api_key': ['OpenAI', 'Anthropic'],
            'browser': ['You', 'Copilot']
        }
    
    def get_working_providers(self) -> List[str]:
        """Get list of providers that are known to work."""
        if self._working_providers_cache is not None:
            return self._working_providers_cache
            
        providers = self.get_all_providers()
        working = [name for name, info in providers.items() if info.get('working', False)]
        
        self._working_providers_cache = working
        return working


def get_providers() -> Dict[str, Any]:
    """Get all available providers."""
    manager = G4FProviderManager()
    return manager.get_all_providers()

def get_models() -> List[str]:
    """Get all available models."""
    manager = G4FProviderManager()
    return manager.get_all_models()

def categorize_by_auth() -> Dict[str, List[str]]:
    """Categorize providers by authentication type."""
    manager = G4FProviderManager()
    return manager.categorize_providers_by_auth()
