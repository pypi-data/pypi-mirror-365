"""Image generation functionality for G4F integration."""

from __future__ import annotations

import logging
import asyncio
import base64
from io import BytesIO
from typing import Any, Dict, List, Optional, Union, Literal
from pathlib import Path

from langchain_core.utils import get_pydantic_field_names
from langchain_core.utils.utils import _build_model_kwargs
from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing_extensions import Self

# Import g4f
try:
    import g4f
    from g4f.client import Client, AsyncClient
    from g4f.Provider import BaseProvider
except ImportError as e:
    raise ImportError(
        "Could not import g4f python package. "
        "Please install it with `pip install g4f`."
    ) from e

# Optional PIL import for image handling
try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

logger = logging.getLogger(__name__)

class ImageGenerationResponse:
    """Response object for image generation."""
    
    def __init__(self, 
                 url: Optional[str] = None, 
                 data: Optional[bytes] = None,
                 alt: Optional[str] = None,
                 prompt: Optional[str] = None,
                 model: Optional[str] = None,
                 provider: Optional[str] = None):
        self.url = url
        self.data = data
        self.alt = alt
        self.prompt = prompt
        self.model = model
        self.provider = provider
    
    def save(self, path: Union[str, Path]) -> None:
        """Save image to file."""
        path = Path(path)
        
        if self.data:
            # Save binary data directly
            with open(path, 'wb') as f:
                f.write(self.data)
        elif self.url:
            # Download from URL
            import requests
            response = requests.get(self.url)
            response.raise_for_status()
            with open(path, 'wb') as f:
                f.write(response.content)
        else:
            raise ValueError("No image data or URL available")
    
    def to_pil(self) -> 'Image.Image':
        """Convert to PIL Image object."""
        if not HAS_PIL:
            raise ImportError("PIL is required for to_pil(). Install with: pip install Pillow")
        
        if self.data:
            return Image.open(BytesIO(self.data))
        elif self.url:
            import requests
            response = requests.get(self.url)
            response.raise_for_status()
            return Image.open(BytesIO(response.content))
        else:
            raise ValueError("No image data or URL available")
    
    def to_base64(self) -> str:
        """Convert image to base64 string."""
        if self.data:
            return base64.b64encode(self.data).decode('utf-8')
        elif self.url:
            import requests
            response = requests.get(self.url)
            response.raise_for_status()
            return base64.b64encode(response.content).decode('utf-8')
        else:
            raise ValueError("No image data or URL available")
    
    def show(self) -> None:
        """Display image using PIL."""
        if not HAS_PIL:
            raise ImportError("PIL is required for show(). Install with: pip install Pillow")
        
        img = self.to_pil()
        img.show()
    
    def __repr__(self) -> str:
        return f"ImageGenerationResponse(url={self.url}, alt='{self.alt}', model='{self.model}', provider='{self.provider}')"

class ImageG4F(BaseModel):
    """G4F Image generation integration.

    This class provides image generation capabilities using the G4F library.

    Setup:
        Install ``g4f`` and optionally set environment variables.

        .. code-block:: bash

            pip install -U g4f

    Key init args:
        model: str
            Name of the image model to use (e.g., "flux", "dall-e-3").
        provider: Any
            G4F provider to use for image generation.
        api_key: Optional[str]
            API key for providers that require authentication.
        response_format: str
            Format for response ("url" or "b64_json").

    Example:
        .. code-block:: python

            from langchain_g4f import ImageG4F
            import g4f

            image_gen = ImageG4F(
                model="flux",
                provider=g4f.Provider.HuggingFaceMedia,
                api_key="your-api-key",
            )

            response = image_gen.generate("a white siamese cat")
            response.save("cat.png")
            response.show()  # Display using PIL
    """

    model_name: str = Field(default="flux", alias="model")
    """Image model name to use."""
    
    provider: Any = Field(default=None)
    """G4F provider to use. If None, g4f will auto-select."""
    
    api_key: Optional[str] = Field(default=None)
    """API key for providers that require authentication."""
    
    response_format: Literal["url", "b64_json"] = "url"
    """Response format for generated images."""
    
    size: Optional[str] = Field(default=None)
    """Image size (e.g., "1024x1024")."""
    
    quality: Optional[str] = Field(default=None)
    """Image quality setting."""
    
    style: Optional[str] = Field(default=None)
    """Image style setting."""
    
    n: int = 1
    """Number of images to generate."""
    
    model_kwargs: Dict[str, Any] = Field(default_factory=dict)
    """Additional parameters for the g4f create call."""

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        exclude={"provider"},
    )

    @model_validator(mode="before")
    @classmethod
    def build_extra(cls, values: Dict[str, Any]) -> Any:
        """Build extra kwargs from additional params that were passed in."""
        all_required_field_names = get_pydantic_field_names(cls)
        values = _build_model_kwargs(values, all_required_field_names)
        return values

    @model_validator(mode="after")
    def validate_environment(self) -> Self:
        """Validate that the g4f library is available."""
        # Validate provider if specified
        if self.provider is not None:
            if not hasattr(self.provider, 'create_completion') and not hasattr(self.provider, 'create_async_generator'):
                logger.warning(f"Provider {self.provider} may not be a valid g4f provider")
        
        return self

    def _prepare_params(self, **kwargs: Any) -> Dict[str, Any]:
        """Prepare parameters for g4f image generation call."""
        params = {
            "model": self.model_name,
            "response_format": self.response_format,
            "n": self.n,
            **self.model_kwargs,
            **kwargs,
        }
        
        if self.size:
            params["size"] = self.size
        if self.quality:
            params["quality"] = self.quality
        if self.style:
            params["style"] = self.style
        if self.provider is not None:
            params["provider"] = self.provider
        if self.api_key is not None:
            params["api_key"] = self.api_key
            
        return params

    def generate(self, 
                 prompt: str, 
                 **kwargs: Any) -> Union[ImageGenerationResponse, List[ImageGenerationResponse]]:
        """Generate image(s) from text prompt.
        
        Args:
            prompt: Text description of the image to generate
            **kwargs: Additional parameters
            
        Returns:
            ImageGenerationResponse or list of responses
        """
        params = self._prepare_params(**kwargs)
        
        try:
            client = Client()
            response = client.images.generate(
                prompt=prompt,
                **params
            )
            
            return self._process_response(response, prompt)
            
        except Exception as e:
            logger.error(f"Error in g4f image generation: {e}")
            raise

    async def agenerate(self, 
                       prompt: str, 
                       **kwargs: Any) -> Union[ImageGenerationResponse, List[ImageGenerationResponse]]:
        """Async generate image(s) from text prompt.
        
        Args:
            prompt: Text description of the image to generate
            **kwargs: Additional parameters
            
        Returns:
            ImageGenerationResponse or list of responses
        """
        params = self._prepare_params(**kwargs)
        
        try:
            client = AsyncClient()
            response = await client.images.generate(
                prompt=prompt,
                **params
            )
            
            return self._process_response(response, prompt)
            
        except Exception as e:
            logger.error(f"Error in g4f async image generation: {e}")
            raise

    def create_variation(self, 
                        image: Union[str, Path, bytes], 
                        prompt: Optional[str] = None,
                        **kwargs: Any) -> Union[ImageGenerationResponse, List[ImageGenerationResponse]]:
        """Create variations of an existing image.
        
        Args:
            image: Source image (file path, URL, or bytes)
            prompt: Optional prompt for variation
            **kwargs: Additional parameters
            
        Returns:
            ImageGenerationResponse or list of responses
        """
        params = self._prepare_params(**kwargs)
        
        try:
            client = Client()
            response = client.images.create_variation(
                image=image,
                prompt=prompt,
                **params
            )
            
            return self._process_response(response, prompt or "Image variation")
            
        except Exception as e:
            logger.error(f"Error in g4f image variation: {e}")
            raise

    async def acreate_variation(self, 
                               image: Union[str, Path, bytes], 
                               prompt: Optional[str] = None,
                               **kwargs: Any) -> Union[ImageGenerationResponse, List[ImageGenerationResponse]]:
        """Async create variations of an existing image.
        
        Args:
            image: Source image (file path, URL, or bytes)
            prompt: Optional prompt for variation
            **kwargs: Additional parameters
            
        Returns:
            ImageGenerationResponse or list of responses
        """
        params = self._prepare_params(**kwargs)
        
        try:
            client = AsyncClient()
            response = await client.images.create_variation(
                image=image,
                prompt=prompt,
                **params
            )
            
            return self._process_response(response, prompt or "Image variation")
            
        except Exception as e:
            logger.error(f"Error in g4f async image variation: {e}")
            raise

    def _process_response(self, response: Any, prompt: str) -> Union[ImageGenerationResponse, List[ImageGenerationResponse]]:
        """Process the response from g4f image generation."""
        results = []
        
        try:
            # Handle different response formats
            if hasattr(response, 'data') and response.data:
                # Standard OpenAI-like response
                for item in response.data:
                    if hasattr(item, 'url') and item.url:
                        result = ImageGenerationResponse(
                            url=item.url,
                            alt=prompt,
                            prompt=prompt,
                            model=self.model_name,
                            provider=str(self.provider) if self.provider else None
                        )
                    elif hasattr(item, 'b64_json') and item.b64_json:
                        # Base64 encoded image
                        data = base64.b64decode(item.b64_json)
                        result = ImageGenerationResponse(
                            data=data,
                            alt=prompt,
                            prompt=prompt,
                            model=self.model_name,
                            provider=str(self.provider) if self.provider else None
                        )
                    else:
                        # Fallback - convert item to string (might be URL)
                        result = ImageGenerationResponse(
                            url=str(item),
                            alt=prompt,
                            prompt=prompt,
                            model=self.model_name,
                            provider=str(self.provider) if self.provider else None
                        )
                    results.append(result)
            
            elif hasattr(response, 'url'):
                # Direct URL response
                result = ImageGenerationResponse(
                    url=response.url,
                    alt=prompt,
                    prompt=prompt,
                    model=self.model_name,
                    provider=str(self.provider) if self.provider else None
                )
                results.append(result)
            
            elif isinstance(response, str):
                # Simple string URL response
                result = ImageGenerationResponse(
                    url=response,
                    alt=prompt,
                    prompt=prompt,
                    model=self.model_name,
                    provider=str(self.provider) if self.provider else None
                )
                results.append(result)
            
            else:
                # Fallback - try to convert to string
                result = ImageGenerationResponse(
                    url=str(response),
                    alt=prompt,
                    prompt=prompt,
                    model=self.model_name,
                    provider=str(self.provider) if self.provider else None
                )
                results.append(result)
        
        except Exception as e:
            logger.error(f"Error processing image response: {e}")
            # Create a fallback response
            result = ImageGenerationResponse(
                url=str(response) if response else None,
                alt=prompt,
                prompt=prompt,
                model=self.model_name,
                provider=str(self.provider) if self.provider else None
            )
            results.append(result)
        
        # Return single result or list based on number generated
        if self.n == 1:
            return results[0] if results else ImageGenerationResponse(prompt=prompt, model=self.model_name)
        else:
            return results

    @classmethod
    def get_available_models(cls) -> List[str]:
        """Get list of available image generation models.
        
        Returns:
            List of model names that support image generation
        """
        try:
            from .utils import G4FUtils
            models = G4FUtils.get_image_generation_models()
            return [model.name for model in models]
        except ImportError:
            # Fallback list of common image models
            return [
                "flux", "flux-pro", "flux-dev", "flux-schnell",
                "dall-e-3", "gpt-image", 
                "sdxl-1.0", "sdxl-turbo", "sd-3.5-large",
                "midjourney"
            ]

    @classmethod
    def get_available_providers(cls) -> List[str]:
        """Get list of providers that support image generation.
        
        Returns:
            List of provider names that support image generation
        """
        try:
            from .utils import G4FUtils
            providers = G4FUtils.get_providers_by_capability(images=True)
            return [provider.name for provider in providers]
        except ImportError:
            # Fallback list of common image providers
            return [
                "HuggingFaceMedia", "PollinationsAI", "OpenaiChat",
                "Copilot", "Gemini", "You", "MicrosoftDesigner"
            ]

# Convenience functions
def generate_image(prompt: str, 
                  model: str = "flux",
                  provider: Optional[Any] = None,
                  **kwargs) -> ImageGenerationResponse:
    """Generate a single image from text prompt.
    
    Args:
        prompt: Text description of the image
        model: Image model to use
        provider: G4F provider to use
        **kwargs: Additional parameters
        
    Returns:
        ImageGenerationResponse object
    """
    image_gen = ImageG4F(model=model, provider=provider, **kwargs)
    return image_gen.generate(prompt)

async def agenerate_image(prompt: str, 
                         model: str = "flux",
                         provider: Optional[Any] = None,
                         **kwargs) -> ImageGenerationResponse:
    """Async generate a single image from text prompt.
    
    Args:
        prompt: Text description of the image
        model: Image model to use
        provider: G4F provider to use
        **kwargs: Additional parameters
        
    Returns:
        ImageGenerationResponse object
    """
    image_gen = ImageG4F(model=model, provider=provider, **kwargs)
    return await image_gen.agenerate(prompt)

def batch_generate_images(prompts: List[str], 
                         model: str = "flux",
                         provider: Optional[Any] = None,
                         **kwargs) -> List[ImageGenerationResponse]:
    """Generate multiple images from text prompts.
    
    Args:
        prompts: List of text descriptions
        model: Image model to use
        provider: G4F provider to use
        **kwargs: Additional parameters
        
    Returns:
        List of ImageGenerationResponse objects
    """
    image_gen = ImageG4F(model=model, provider=provider, **kwargs)
    results = []
    
    for prompt in prompts:
        try:
            result = image_gen.generate(prompt)
            results.append(result)
        except Exception as e:
            logger.error(f"Error generating image for prompt '{prompt}': {e}")
            # Add a failed response
            results.append(ImageGenerationResponse(prompt=prompt, model=model))
    
    return results

async def abatch_generate_images(prompts: List[str], 
                                model: str = "flux",
                                provider: Optional[Any] = None,
                                **kwargs) -> List[ImageGenerationResponse]:
    """Async generate multiple images from text prompts.
    
    Args:
        prompts: List of text descriptions
        model: Image model to use
        provider: G4F provider to use
        **kwargs: Additional parameters
        
    Returns:
        List of ImageGenerationResponse objects
    """
    image_gen = ImageG4F(model=model, provider=provider, **kwargs)
    
    async def generate_single(prompt: str) -> ImageGenerationResponse:
        try:
            return await image_gen.agenerate(prompt)
        except Exception as e:
            logger.error(f"Error generating image for prompt '{prompt}': {e}")
            return ImageGenerationResponse(prompt=prompt, model=model)
    
    # Generate all images concurrently
    tasks = [generate_single(prompt) for prompt in prompts]
    return await asyncio.gather(*tasks)


class G4FImageGenerator:
    """High-level interface for G4F image generation."""
    
    def __init__(self, model: str = "flux", provider: Optional[Any] = None, **kwargs):
        """Initialize image generator.
        
        Args:
            model: Image model to use
            provider: G4F provider to use
            **kwargs: Additional parameters
        """
        self.model = model
        self.provider = provider
        self.kwargs = kwargs
        self._generator = ImageG4F(model=model, provider=provider, **kwargs)
    
    def generate(self, prompt: str) -> ImageGenerationResponse:
        """Generate image from text prompt.
        
        Args:
            prompt: Text description of the image to generate
            
        Returns:
            ImageGenerationResponse object
        """
        return self._generator.generate(prompt)
    
    async def agenerate(self, prompt: str) -> ImageGenerationResponse:
        """Async generate image from text prompt.
        
        Args:
            prompt: Text description of the image to generate
            
        Returns:
            ImageGenerationResponse object
        """
        return await self._generator.agenerate(prompt)
    
    def batch_generate(self, prompts: List[str]) -> List[ImageGenerationResponse]:
        """Generate multiple images from text prompts.
        
        Args:
            prompts: List of text descriptions
            
        Returns:
            List of ImageGenerationResponse objects
        """
        return batch_generate_images(prompts, self.model, self.provider, **self.kwargs)
    
    async def abatch_generate(self, prompts: List[str]) -> List[ImageGenerationResponse]:
        """Async generate multiple images from text prompts.
        
        Args:
            prompts: List of text descriptions
            
        Returns:
            List of ImageGenerationResponse objects
        """
        return await abatch_generate_images(prompts, self.model, self.provider, **self.kwargs)
