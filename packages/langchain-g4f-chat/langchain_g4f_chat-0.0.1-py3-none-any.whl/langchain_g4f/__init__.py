"""langchain-g4f: Comprehensive G4F integration for LangChain with all capabilities."""

# Core functionality
try:
    from langchain_g4f.core import get_providers, get_models, categorize_by_auth, AuthType
except ImportError:
    # Fallback imports
    from langchain_g4f.core.providers import get_providers, get_models, categorize_by_auth
    from langchain_g4f.core.authentication import AuthType

# Text generation
from langchain_g4f.text import ChatG4F

# Image capabilities
try:
    from langchain_g4f.images import ImageG4F, generate_image, edit_image, enhance_image
except ImportError:
    # Individual imports as fallback
    from langchain_g4f.images.image_generation import ImageG4F, generate_image
  

__all__ = [
    # Core
    "get_providers",
    "get_models", 
    "categorize_by_auth",
    "AuthType",
    # Text
    "ChatG4F",
    # Images
    "ImageG4F",
    "generate_image",
  ]
