# LangChain G4F - Enhanced GPT-4 Free Integration

A comprehensive Python package that integrates G4F (GPT4Free) with LangChain, providing free access to various AI models including chat, image generation, vision, and media processing capabilities.

## 📑 Table of Contents

- [Features](#-features)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Use Cases](#-use-cases)
- [Authentication](#-authentication)
- [Provider Categories](#-provider-categories)
- [Testing](#-testing)
- [Examples](#-examples)
- [API Reference](#%EF%B8%8F-api-reference)
- [Advanced Usage](#-advanced-usage)
- [Contributing](#-contributing)
- [License](#-license)
- [Support](#-support)

## 🚀 Features

### Core Chat Functionality
- **Multi-Model Support**: Access to GPT-4, GPT-3.5, Claude, Gemini, and more
- **Provider Management**: 80+ providers with authentication categorization
- **Vision Support**: Chat with images using vision-capable models
- **Streaming**: Real-time response streaming
- **Async Support**: Full async/await compatibility

### Image Generation
- **Multiple Models**: Flux, DALL-E, Stable Diffusion, and more
- **Batch Processing**: Generate multiple images asynchronously
- **Format Support**: URL, base64, PIL image objects
- **Style Control**: Size, style, and quality parameters

### Media Processing
- **Audio Generation**: Text-to-speech with multiple voices
- **Audio Transcription**: Speech-to-text conversion
- **Video Generation**: Text-to-video capabilities
- **File Processing**: Upload and analyze various file types

### Provider Intelligence
- **Authentication Categorization**: API key, cookies, HAR files, no-auth
- **Capability Detection**: Text, images, vision, audio support
- **Working Status**: Real-time provider availability
- **Smart Recommendations**: Best providers for specific use cases

## 📦 Installation

```bash
# Install from local directory
pip install -e .

# Install dependencies
pip install g4f langchain-core pillow aiohttp requests langchain-g4f-chat
```
## 🔧 Quick Start

### Basic Chat

```python
from langchain_g4f import ChatG4F
import g4f.Provider as Provider

# Initialize chat model
llm = ChatG4F(
    model="gpt-4o-mini",
    provider=Provider.Blackbox,  # No auth required
    temperature=0.7
)

# Chat
messages = [
    ("system", "You are a helpful assistant."),
    ("human", "What is machine learning?")
]

response = llm.invoke(messages)
print(response.content)
```

### Image Generation

```python
from langchain_g4f import generate_image
import g4f.Provider as Provider

# Generate image
response = generate_image(
    "a beautiful sunset over mountains",
    model="flux",
    provider=Provider.PollinationsAI
)

print(f"Image URL: {response.url}")
response.save("sunset.png")  # Save locally
response.show()  # Display with PIL
```

### Vision Chat

```python
# Chat with image
messages = [
    ("human", [
        {"type": "text", "text": "What's in this image?"},
        {"type": "image_url", "image_url": {"url": "https://example.com/image.jpg"}}
    ])
]

response = llm.invoke(messages)
print(response.content)
```

### Provider Discovery

```python
from langchain_g4f import G4FUtils, get_providers

# Get providers by authentication
no_auth_providers = G4FUtils.get_providers_by_auth(needs_auth=False)
print(f"No-auth providers: {len(no_auth_providers)}")

# Get providers by capability
image_providers = G4FUtils.get_providers_by_capability(images=True)
vision_providers = G4FUtils.get_providers_by_capability(vision=True)

# Get working providers
working_providers = get_providers(working=True)
```
## 🎯 Use Cases

### 1. Content Creation Workflow

```python
import asyncio
from langchain_g4f import generate_image, quick_image_analyze, ChatG4F

async def content_workflow():
    # Generate image
    image = generate_image("modern office space")
    
    # Analyze image
    analysis = await quick_image_analyze(
        image.url, 
        "Describe the atmosphere and design elements"
    )
    
    # Create content
    llm = ChatG4F(model="gpt-4o-mini")
    content = llm.invoke([
        ("human", f"Write a blog post about this office: {analysis}")
    ])
    
    return image, analysis, content

# Run workflow
image, analysis, content = asyncio.run(content_workflow())
```

### 2. Multi-Modal Analysis

```python
from langchain_g4f import MediaProcessorG4F

processor = MediaProcessorG4F()

# Batch process different media types
items = [
    {"type": "vision", "image": "photo.jpg", "query": "Analyze this image"},
    {"type": "audio", "text": "Create narration", "voice": "alloy"},
    {"type": "video", "prompt": "A spinning globe", "resolution": "720p"}
]

results = await processor.batch_process_media(items)
```

### 3. Provider Optimization

```python
from langchain_g4f import G4FUtils

# Find best providers for your needs
def get_optimal_provider(use_case):
    if use_case == "chat":
        providers = G4FUtils.get_providers_by_auth(needs_auth=False)
        return [p for p in providers if p.working and p.supports_text][:3]
    
    elif use_case == "images":
        providers = G4FUtils.get_providers_by_capability(images=True)
        return [p for p in providers if p.working][:3]
    
    elif use_case == "vision":
        providers = G4FUtils.get_providers_by_capability(vision=True)
        return [p for p in providers if p.working][:3]

# Get recommendations
chat_providers = get_optimal_provider("chat")
image_providers = get_optimal_provider("images")
```
## 🔐 Authentication

Different providers require different authentication methods:

### No Authentication Required

```python
# These providers work without any setup
Provider.Blackbox      # Chat, code
Provider.PollinationsAI  # Images, audio
Provider.FreeGpt       # Basic chat
```

### API Key Authentication

```python
# Set environment variables
import os

os.environ["OPENAI_API_KEY"] = "your-key"
os.environ["GEMINI_API_KEY"] = "your-key"
os.environ["HF_TOKEN"] = "your-token"

# Use with providers
ChatG4F(provider=Provider.OpenaiChat, api_key=os.getenv("OPENAI_API_KEY"))
```

### Cookie/Session Authentication

```python
# Some providers need browser cookies
# Check G4F documentation for setup
```
## 📊 Provider Categories

### By Authentication Type
- **No Auth**: 45+ providers (Blackbox, FreeGpt, PollinationsAI, etc.)
- **API Key**: 20+ providers (OpenAI, Gemini, Anthropic, etc.)
- **Cookies**: 15+ providers (ChatGPT, Bing, Bard, etc.)
- **HAR Files**: 5+ providers (Advanced session management)


### By Capability
- **Text Chat**: 70+ providers
- **Image Generation**: 15+ providers
- **Vision/Image Analysis**: 25+ providers
- **Audio Processing**: 8+ providers
- **File Upload**: 12+ providers


## 🧪 Testing

Run the comprehensive test suite:

```python
# Test utilities
python -m pytest langchain_g4f/test_utils.py -v

# Test image generation
python -m pytest langchain_g4f/test_image_generation.py -v

# Test media processing
python -m pytest langchain_g4f/test_media.py -v

# Run all tests
python -m pytest langchain_g4f/ -v
## 📖 Examples

### Complete Examples

# Run comprehensive examples
python langchain_g4f/example_usage.py
```

### Available Examples

1. **Basic Chat** - Simple Q&A with various models
2. **Vision Chat** - Image analysis and description
3. **Image Generation** - Create images from text
4. **Batch Processing** - Multiple operations simultaneously
5. **Audio Generation** - Text-to-speech conversion
6. **Media Processing** - Multi-modal content handling
7. **Provider Discovery** - Find optimal providers
8. **Workflow Automation** - Complete AI pipelines## 🛠️ API Reference

### Core Classes

#### ChatG4F

```python
class ChatG4F:
    def __init__(self, model, provider, temperature=0.7, **kwargs)
    def invoke(self, messages) -> AIMessage
    async def ainvoke(self, messages) -> AIMessage
    def stream(self, messages) -> Iterator[AIMessageChunk]
```

#### ImageG4F

```python
class ImageG4F:
    def __init__(self, model, provider, **kwargs)
    def generate(self, prompt, **kwargs) -> ImageGenerationResponse
    async def agenerate(self, prompt, **kwargs) -> ImageGenerationResponse
    @staticmethod
    def get_available_models() -> List[str]
```

#### MediaProcessorG4F

```python
class MediaProcessorG4F:
    def __init__(self, provider=None, **kwargs)
    async def generate_audio(self, text, voice="alloy") -> Dict
    async def transcribe_audio(self, audio_file) -> Dict
    async def analyze_image(self, image, query) -> Dict
    async def batch_process_media(self, items) -> List[Dict]
```

#### G4FUtils

```python
class G4FUtils:
    @staticmethod
    def get_providers_by_auth(needs_auth=None) -> List[ProviderInfo]
    @staticmethod
    def get_providers_by_capability(**capabilities) -> List[ProviderInfo]
    @staticmethod
    def get_image_generation_models() -> List[str]
    @staticmethod
    def get_vision_models() -> List[str]
```

### Convenience Functions

```python
# Image generation
generate_image(prompt, model, provider) -> ImageGenerationResponse
batch_generate_images(prompts, **kwargs) -> List[ImageGenerationResponse]

# Media processing
quick_audio_generate(text, voice, provider) -> bytes
quick_image_analyze(image, query, provider) -> str

# Provider discovery
get_providers(working=None, needs_auth=None) -> List[ProviderInfo]
get_models() -> List[str]
print_summary() -> None


## 🔍 Advanced Usage

### Custom Provider Configuration

# Configure provider with specific settings
llm = ChatG4F(
    model="gpt-4",
    provider=Provider.GPTalk,
    temperature=0.3,
    max_tokens=2000,
    top_p=0.9,
    frequency_penalty=0.1
)
```

### Error Handling

```python
from langchain_g4f import ChatG4F, G4FUtils

try:
    # Try primary provider
    llm = ChatG4F(model="gpt-4", provider=Provider.Primary)
    response = llm.invoke(messages)
except Exception:
    # Fallback to reliable provider
    fallback_providers = G4FUtils.get_providers_by_auth(needs_auth=False)
    llm = ChatG4F(model="gpt-3.5-turbo", provider=fallback_providers[0].provider)
    response = llm.invoke(messages)
```

### Performance Optimization

```python
# Use caching for provider information
G4FUtils._cache_timeout = 3600  # Cache for 1 hour

# Batch operations for efficiency
prompts = ["Generate image 1", "Generate image 2", "Generate image 3"]
images = await batch_generate_images(prompts, provider=Provider.PollinationsAI)
```
## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License. See LICENSE file for details.

## 🙏 Acknowledgments

- [G4F (GPT4Free)](https://github.com/xtekky/gpt4free) - Core AI provider integration
- [LangChain](https://github.com/langchain-ai/langchain) - Framework foundation
- All the amazing G4F provider maintainers

## 🆘 Support

- Check the [examples](example_usage.py) for common use cases
- Review [test files](test_*.py) for implementation details
- Open issues for bugs or feature requests
- Join discussions for community support


---

**Made with ❤️ for the open-source AI community**

---

> **Note:** This project is made for educational and learning purposes only. If you are a copyright holder or have any concerns about the content, please contact us politely and we will promptly address your request, including removal if necessary. No legal process is required—just reach out and we will cooperate respectfully.