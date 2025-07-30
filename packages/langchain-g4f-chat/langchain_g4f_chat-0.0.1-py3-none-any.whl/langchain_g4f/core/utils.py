"""Utilities for G4F providers and models information."""

from __future__ import annotations

import logging
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass

# Import g4f
try:
    import g4f
    from g4f.Provider import __providers__, __map__
    from g4f.providers.base_provider import ProviderModelMixin
except ImportError as e:
    raise ImportError(
        "Could not import g4f python package. "
        "Please install it with `pip install g4f`."
    ) from e

logger = logging.getLogger(__name__)

@dataclass
class ProviderInfo:
    """Information about a G4F provider."""
    name: str
    label: str
    url: Optional[str] = None
    working: bool = False
    needs_auth: bool = False
    auth_type: Optional[str] = None
    login_url: Optional[str] = None
    supports_text: bool = True
    supports_images: bool = False
    supports_vision: bool = False
    supports_audio: bool = False
    supports_video: bool = False
    supports_stream: bool = False
    default_model: Optional[str] = None
    models: List[str] = None
    image_models: List[str] = None
    vision_models: List[str] = None
    audio_models: List[str] = None
    video_models: List[str] = None

    def __post_init__(self):
        if self.models is None:
            self.models = []
        if self.image_models is None:
            self.image_models = []
        if self.vision_models is None:
            self.vision_models = []
        if self.audio_models is None:
            self.audio_models = []
        if self.video_models is None:
            self.video_models = []

@dataclass
class ModelInfo:
    """Information about a model."""
    name: str
    provider: str
    supports_vision: bool = False
    supports_audio: bool = False
    supports_video: bool = False
    supports_image_generation: bool = False
    needs_auth: bool = False
    is_default: bool = False

class G4FUtils:
    """Utility class for G4F providers and models information."""
    
    _providers_cache: Optional[List[ProviderInfo]] = None
    _models_cache: Optional[List[ModelInfo]] = None
    
    @classmethod
    def get_providers(cls, force_refresh: bool = False) -> List[ProviderInfo]:
        """Get list of all available providers with their information.
        
        Args:
            force_refresh: Force refresh the cache
            
        Returns:
            List of ProviderInfo objects
        """
        if cls._providers_cache is None or force_refresh:
            cls._providers_cache = cls._fetch_providers()
        return cls._providers_cache
    
    @classmethod
    def get_providers_by_auth(cls, needs_auth: Optional[bool] = None) -> List[ProviderInfo]:
        """Get providers filtered by authentication requirement.
        
        Args:
            needs_auth: True for auth required, False for no auth, None for all
            
        Returns:
            Filtered list of ProviderInfo objects
        """
        providers = cls.get_providers()
        if needs_auth is None:
            return providers
        return [p for p in providers if p.needs_auth == needs_auth]
    
    @classmethod
    def get_providers_by_capability(cls, 
                                  text: bool = False,
                                  images: bool = False, 
                                  vision: bool = False,
                                  audio: bool = False,
                                  video: bool = False) -> List[ProviderInfo]:
        """Get providers filtered by capabilities.
        
        Args:
            text: Support text generation
            images: Support image generation  
            vision: Support image understanding
            audio: Support audio generation
            video: Support video generation
            
        Returns:
            Filtered list of ProviderInfo objects
        """
        providers = cls.get_providers()
        filtered = []
        
        for provider in providers:
            match = True
            if text and not provider.supports_text:
                match = False
            if images and not provider.supports_images:
                match = False
            if vision and not provider.supports_vision:
                match = False
            if audio and not provider.supports_audio:
                match = False
            if video and not provider.supports_video:
                match = False
            
            if match:
                filtered.append(provider)
                
        return filtered
    
    @classmethod
    def get_working_providers(cls) -> List[ProviderInfo]:
        """Get only working providers.
        
        Returns:
            List of working ProviderInfo objects
        """
        providers = cls.get_providers()
        return [p for p in providers if p.working]
    
    @classmethod
    def get_provider_by_name(cls, name: str) -> Optional[ProviderInfo]:
        """Get provider information by name.
        
        Args:
            name: Provider name
            
        Returns:
            ProviderInfo object or None if not found
        """
        providers = cls.get_providers()
        for provider in providers:
            if provider.name.lower() == name.lower():
                return provider
        return None
    
    @classmethod
    def get_models(cls, provider_name: Optional[str] = None, force_refresh: bool = False) -> List[ModelInfo]:
        """Get list of all available models.
        
        Args:
            provider_name: Filter by specific provider name
            force_refresh: Force refresh the cache
            
        Returns:
            List of ModelInfo objects
        """
        if cls._models_cache is None or force_refresh:
            cls._models_cache = cls._fetch_models()
        
        models = cls._models_cache
        if provider_name:
            models = [m for m in models if m.provider.lower() == provider_name.lower()]
        
        return models
    
    @classmethod
    def get_models_by_capability(cls, 
                               vision: bool = False,
                               audio: bool = False,
                               video: bool = False,
                               image_generation: bool = False,
                               needs_auth: Optional[bool] = None) -> List[ModelInfo]:
        """Get models filtered by capabilities.
        
        Args:
            vision: Support vision/image understanding
            audio: Support audio processing
            video: Support video processing
            image_generation: Support image generation
            needs_auth: Filter by auth requirement
            
        Returns:
            Filtered list of ModelInfo objects
        """
        models = cls.get_models()
        filtered = []
        
        for model in models:
            match = True
            if vision and not model.supports_vision:
                match = False
            if audio and not model.supports_audio:
                match = False
            if video and not model.supports_video:
                match = False
            if image_generation and not model.supports_image_generation:
                match = False
            if needs_auth is not None and model.needs_auth != needs_auth:
                match = False
            
            if match:
                filtered.append(model)
                
        return filtered
    
    @classmethod
    def get_image_generation_models(cls) -> List[ModelInfo]:
        """Get all models that support image generation.
        
        Returns:
            List of ModelInfo objects that support image generation
        """
        return cls.get_models_by_capability(image_generation=True)
    
    @classmethod
    def get_vision_models(cls) -> List[ModelInfo]:
        """Get all models that support vision/image understanding.
        
        Returns:
            List of ModelInfo objects that support vision
        """
        return cls.get_models_by_capability(vision=True)
    
    @classmethod
    def _fetch_providers(cls) -> List[ProviderInfo]:
        """Fetch provider information from g4f."""
        providers = []
        
        try:
            for provider_class in __providers__:
                if not hasattr(provider_class, '__name__'):
                    continue
                    
                try:
                    info = cls._extract_provider_info(provider_class)
                    providers.append(info)
                except Exception as e:
                    logger.warning(f"Error extracting info for provider {getattr(provider_class, '__name__', 'Unknown')}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error fetching providers: {e}")
            
        return providers
    
    @classmethod
    def _extract_provider_info(cls, provider_class) -> ProviderInfo:
        """Extract information from a provider class."""
        name = provider_class.__name__
        
        # Basic info
        label = getattr(provider_class, 'label', name)
        url = getattr(provider_class, 'url', None)
        working = getattr(provider_class, 'working', False)
        needs_auth = getattr(provider_class, 'needs_auth', False)
        login_url = getattr(provider_class, 'login_url', None)
        supports_stream = getattr(provider_class, 'supports_stream', False)
        
        # Determine auth type
        auth_type = None
        if needs_auth:
            if hasattr(provider_class, 'use_nodriver') and provider_class.use_nodriver:
                auth_type = "nodriver"
            elif login_url and "api" in login_url.lower():
                auth_type = "api_key"
            elif login_url:
                auth_type = "cookies"
            else:
                auth_type = "unknown"
        
        # Models and capabilities
        default_model = getattr(provider_class, 'default_model', None)
        
        # Get models safely
        models = []
        image_models = []
        vision_models = []
        audio_models = []
        video_models = []
        
        try:
            if hasattr(provider_class, 'get_models') and callable(provider_class.get_models):
                models = provider_class.get_models() or []
            elif hasattr(provider_class, 'models'):
                models = provider_class.models or []
        except Exception as e:
            logger.debug(f"Could not get models for {name}: {e}")
            models = []
        
        # Image models
        try:
            image_models = getattr(provider_class, 'image_models', []) or []
        except Exception:
            image_models = []
        
        # Vision models
        try:
            vision_models = getattr(provider_class, 'vision_models', []) or []
        except Exception:
            vision_models = []
        
        # Audio models
        try:
            audio_models = getattr(provider_class, 'audio_models', []) or []
        except Exception:
            audio_models = []
        
        # Video models
        try:
            video_models = getattr(provider_class, 'video_models', []) or []
        except Exception:
            video_models = []
        
        # Determine capabilities
        supports_images = len(image_models) > 0
        supports_vision = len(vision_models) > 0 or getattr(provider_class, 'default_vision_model', None) is not None
        supports_audio = len(audio_models) > 0
        supports_video = len(video_models) > 0
        
        return ProviderInfo(
            name=name,
            label=label,
            url=url,
            working=working,
            needs_auth=needs_auth,
            auth_type=auth_type,
            login_url=login_url,
            supports_text=len(models) > 0,
            supports_images=supports_images,
            supports_vision=supports_vision,
            supports_audio=supports_audio,
            supports_video=supports_video,
            supports_stream=supports_stream,
            default_model=default_model,
            models=models,
            image_models=image_models,
            vision_models=vision_models,
            audio_models=audio_models,
            video_models=video_models
        )
    
    @classmethod
    def _fetch_models(cls) -> List[ModelInfo]:
        """Fetch model information from all providers."""
        models = []
        providers = cls.get_providers()
        
        for provider in providers:
            # Add text models
            for model_name in provider.models:
                model_info = ModelInfo(
                    name=model_name,
                    provider=provider.name,
                    supports_vision=model_name in provider.vision_models,
                    supports_audio=model_name in provider.audio_models,
                    supports_video=model_name in provider.video_models,
                    supports_image_generation=model_name in provider.image_models,
                    needs_auth=provider.needs_auth,
                    is_default=model_name == provider.default_model
                )
                models.append(model_info)
            
            # Add image models (if not already included)
            for model_name in provider.image_models:
                if model_name not in provider.models:
                    model_info = ModelInfo(
                        name=model_name,
                        provider=provider.name,
                        supports_vision=False,
                        supports_audio=False,
                        supports_video=False,
                        supports_image_generation=True,
                        needs_auth=provider.needs_auth,
                        is_default=False
                    )
                    models.append(model_info)
        
        return models
    
    @classmethod
    def print_providers_summary(cls):
        """Print a summary of all providers."""
        providers = cls.get_providers()
        working_providers = cls.get_working_providers()
        auth_required = cls.get_providers_by_auth(needs_auth=True)
        no_auth = cls.get_providers_by_auth(needs_auth=False)
        image_providers = cls.get_providers_by_capability(images=True)
        vision_providers = cls.get_providers_by_capability(vision=True)
        
        print("=== G4F Providers Summary ===")
        print(f"Total providers: {len(providers)}")
        print(f"Working providers: {len(working_providers)}")
        print(f"Auth required: {len(auth_required)}")
        print(f"No auth required: {len(no_auth)}")
        print(f"Image generation: {len(image_providers)}")
        print(f"Vision support: {len(vision_providers)}")
        
        print("\n=== Working Providers by Auth Type ===")
        auth_types = {}
        for provider in working_providers:
            auth_type = "No Auth" if not provider.needs_auth else (provider.auth_type or "Unknown")
            if auth_type not in auth_types:
                auth_types[auth_type] = []
            auth_types[auth_type].append(provider.name)
        
        for auth_type, provider_names in auth_types.items():
            print(f"\n{auth_type} ({len(provider_names)}):")
            for name in sorted(provider_names):
                print(f"  - {name}")
    
    @classmethod
    def print_models_summary(cls):
        """Print a summary of all models."""
        models = cls.get_models()
        image_models = cls.get_image_generation_models()
        vision_models = cls.get_vision_models()
        
        # Group by provider
        provider_models = {}
        for model in models:
            if model.provider not in provider_models:
                provider_models[model.provider] = []
            provider_models[model.provider].append(model)
        
        print("=== G4F Models Summary ===")
        print(f"Total models: {len(models)}")
        print(f"Image generation models: {len(image_models)}")
        print(f"Vision models: {len(vision_models)}")
        print(f"Providers with models: {len(provider_models)}")
        
        print("\n=== Models by Provider ===")
        for provider_name in sorted(provider_models.keys()):
            provider_model_list = provider_models[provider_name]
            print(f"\n{provider_name} ({len(provider_model_list)} models):")
            
            # Group by capability
            text_models = [m for m in provider_model_list if not m.supports_image_generation]
            img_models = [m for m in provider_model_list if m.supports_image_generation]
            
            if text_models:
                print(f"  Text: {', '.join([m.name for m in text_models[:5]])}" + 
                      (f" ... (+{len(text_models)-5} more)" if len(text_models) > 5 else ""))
            
            if img_models:
                print(f"  Image: {', '.join([m.name for m in img_models])}")


def get_providers(**filters) -> List[ProviderInfo]:
    """Get providers with optional filters.
    
    Args:
        **filters: Keyword arguments for filtering (working, needs_auth, supports_images, etc.)
        
    Returns:
        List of filtered ProviderInfo objects
    """
    providers = G4FUtils.get_providers()
    
    for key, value in filters.items():
        if hasattr(ProviderInfo, key):
            providers = [p for p in providers if getattr(p, key) == value]
    
    return providers

def get_models(**filters) -> List[ModelInfo]:
    """Get models with optional filters.
    
    Args:
        **filters: Keyword arguments for filtering (provider, supports_vision, etc.)
        
    Returns:
        List of filtered ModelInfo objects
    """
    models = G4FUtils.get_models()
    
    for key, value in filters.items():
        if hasattr(ModelInfo, key):
            models = [m for m in models if getattr(m, key) == value]
    
    return models

def print_summary():
    """Print a summary of providers and models."""
    G4FUtils.print_providers_summary()
    print("\n" + "="*50 + "\n")
    G4FUtils.print_models_summary()
