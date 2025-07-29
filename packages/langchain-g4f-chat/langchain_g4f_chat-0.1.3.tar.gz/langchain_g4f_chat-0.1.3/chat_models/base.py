"""GPT4Free chat wrapper."""

from __future__ import annotations

import logging
import sys
from collections.abc import AsyncIterator, Iterator, Mapping, Sequence
from typing import (
    Any,
    Callable,
    Literal,
    Optional,
    Union,
    cast,
)

from langchain_core.callbacks import (
    AsyncCallbackManagerForLLMRun,
    CallbackManagerForLLMRun,
)
from langchain_core.language_models import LanguageModelInput
from langchain_core.language_models.chat_models import (
    BaseChatModel,
    agenerate_from_stream,
    generate_from_stream,
)
from langchain_core.messages import (
    AIMessage,
    AIMessageChunk,
    BaseMessage,
    BaseMessageChunk,
    ChatMessage,
    HumanMessage,
    SystemMessage,
)
from langchain_core.outputs import ChatGeneration, ChatGenerationChunk, ChatResult
from langchain_core.utils import get_pydantic_field_names
from langchain_core.utils.utils import _build_model_kwargs, secret_from_env
from pydantic import ConfigDict, Field, SecretStr, model_validator
from typing_extensions import Self

# Import g4f
try:
    import g4f
    from g4f.Provider import BaseProvider
except ImportError as e:
    raise ImportError(
        "Could not import g4f python package. "
        "Please install it with `pip install g4f`."
    ) from e

logger = logging.getLogger(__name__)


def _convert_message_to_dict(message: BaseMessage) -> dict:
    """Convert a LangChain message to a dictionary for g4f.

    Args:
        message: The LangChain message.

    Returns:
        The dictionary.
    """
    message_dict: dict[str, Any] = {"content": message.content}

    # Map LangChain message types to OpenAI format
    if isinstance(message, ChatMessage):
        message_dict["role"] = message.role
    elif isinstance(message, HumanMessage):
        message_dict["role"] = "user"
    elif isinstance(message, AIMessage):
        message_dict["role"] = "assistant"
    elif isinstance(message, SystemMessage):
        message_dict["role"] = "system"
    else:
        raise ValueError(f"Got unknown type {type(message)}")

    return message_dict


def _convert_chunk_to_generation_chunk(chunk: str) -> ChatGenerationChunk:
    """Convert a chunk to a generation chunk."""
    return ChatGenerationChunk(
        message=AIMessageChunk(content=chunk),
        generation_info=None,
    )


class ChatG4F(BaseChatModel):
    """GPT4Free chat model integration.

    This class provides a LangChain interface for the GPT4Free library,
    allowing you to use any g4f provider with LangChain.

    Setup:
        Install ``g4f`` and optionally set environment variables.

        .. code-block:: bash

            pip install -U g4f

    Key init args:
        model: str
            Name of the model to use (e.g., "gpt-3.5-turbo", "gpt-4").
        provider: Any
            G4F provider to use (e.g., g4f.Provider.OpenAI, g4f.Provider.Bing).
        api_key: Optional[str]
            API key for providers that require authentication.
        temperature: float
            Sampling temperature.
        stream: bool
            Whether to stream responses.

    Example:
        .. code-block:: python

            from langchain_g4f import ChatG4F
            import g4f

            llm = ChatG4F(
                model="gpt-3.5-turbo",
                provider=g4f.Provider.OpenAI,
                api_key="your-api-key",
                temperature=0.7,
            )

            messages = [("human", "Hello, how are you?")]
            response = llm.invoke(messages)
    """

    model_name: str = Field(default="gpt-3.5-turbo", alias="model")
    """Model name to use."""
    
    provider: Any = Field(default=None)
    """G4F provider to use. If None, g4f will auto-select."""
    
    api_key: Optional[SecretStr] = Field(default=None)
    """API key for providers that require authentication."""
    
    temperature: float = 0.7
    """What sampling temperature to use."""
    
    max_tokens: Optional[int] = None
    """The maximum number of tokens to generate."""
    
    stream: bool = False
    """Whether to stream the results."""
    
    model_kwargs: dict[str, Any] = Field(default_factory=dict)
    """Holds any additional parameters for the g4f create call."""

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        exclude={"provider"},
    )

    @model_validator(mode="before")
    @classmethod
    def build_extra(cls, values: dict[str, Any]) -> Any:
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

    @property
    def _llm_type(self) -> str:
        """Return type of llm."""
        return "g4f"

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        provider_name = getattr(self.provider, '__name__', str(self.provider)) if self.provider else None
        return {
            "model_name": self.model_name,
            "provider": provider_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stream": self.stream,
            **self.model_kwargs,
        }

    def _prepare_params(self, **kwargs: Any) -> dict[str, Any]:
        """Prepare parameters for g4f call."""
        params = {
            "model": self.model_name,
            "temperature": self.temperature,
            "stream": self.stream,
            **self.model_kwargs,
            **kwargs,
        }
        
        if self.max_tokens is not None:
            params["max_tokens"] = self.max_tokens
            
        if self.provider is not None:
            params["provider"] = self.provider
            
        if self.api_key is not None:
            params["api_key"] = self.api_key.get_secret_value()
            
        return params

    def _stream(
        self,
        messages: list[BaseMessage],
        stop: Optional[list[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        """Stream the LLM on the given messages."""
        params = self._prepare_params(stream=True, **kwargs)
        messages_dict = [_convert_message_to_dict(m) for m in messages]
        
        try:
            response = g4f.ChatCompletion.create(
                messages=messages_dict,
                **params
            )
            
            # Handle streaming response
            if hasattr(response, '__iter__'):
                for chunk in response:
                    if chunk:
                        generation_chunk = _convert_chunk_to_generation_chunk(chunk)
                        if run_manager:
                            run_manager.on_llm_new_token(chunk, chunk=generation_chunk)
                        yield generation_chunk
            else:
                # Non-streaming response
                generation_chunk = _convert_chunk_to_generation_chunk(str(response))
                if run_manager:
                    run_manager.on_llm_new_token(str(response), chunk=generation_chunk)
                yield generation_chunk
                
        except Exception as e:
            logger.error(f"Error in g4f streaming: {e}")
            raise

    async def _astream(
        self,
        messages: list[BaseMessage],
        stop: Optional[list[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> AsyncIterator[ChatGenerationChunk]:
        """Async stream the LLM on the given messages."""
        params = self._prepare_params(stream=True, **kwargs)
        messages_dict = [_convert_message_to_dict(m) for m in messages]
        
        try:
            response = await g4f.ChatCompletion.create_async(
                messages=messages_dict,
                **params
            )
            
            # Handle async streaming response
            if hasattr(response, '__aiter__'):
                async for chunk in response:
                    if chunk:
                        generation_chunk = _convert_chunk_to_generation_chunk(chunk)
                        if run_manager:
                            await run_manager.on_llm_new_token(chunk, chunk=generation_chunk)
                        yield generation_chunk
            else:
                # Non-streaming response
                generation_chunk = _convert_chunk_to_generation_chunk(str(response))
                if run_manager:
                    await run_manager.on_llm_new_token(str(response), chunk=generation_chunk)
                yield generation_chunk
                
        except Exception as e:
            logger.error(f"Error in g4f async streaming: {e}")
            raise

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: Optional[list[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Call g4f and return the response."""
        if self.stream:
            stream_iter = self._stream(
                messages, stop=stop, run_manager=run_manager, **kwargs
            )
            return generate_from_stream(stream_iter)

        params = self._prepare_params(stream=False, **kwargs)
        messages_dict = [_convert_message_to_dict(m) for m in messages]
        
        try:
            response = g4f.ChatCompletion.create(
                messages=messages_dict,
                **params
            )
            
            # Convert response to ChatResult
            message = AIMessage(content=str(response))
            generation = ChatGeneration(message=message)
            
            return ChatResult(
                generations=[generation],
                llm_output={
                    "model_name": self.model_name,
                    "provider": str(self.provider) if self.provider else None,
                },
            )
            
        except Exception as e:
            logger.error(f"Error in g4f generation: {e}")
            raise

    async def _agenerate(
        self,
        messages: list[BaseMessage],
        stop: Optional[list[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Async call g4f and return the response."""
        if self.stream:
            stream_iter = self._astream(
                messages, stop=stop, run_manager=run_manager, **kwargs
            )
            return await agenerate_from_stream(stream_iter)

        params = self._prepare_params(stream=False, **kwargs)
        messages_dict = [_convert_message_to_dict(m) for m in messages]
        
        try:
            response = await g4f.ChatCompletion.create_async(
                messages=messages_dict,
                **params
            )
            
            # Convert response to ChatResult
            message = AIMessage(content=str(response))
            generation = ChatGeneration(message=message)
            
            return ChatResult(
                generations=[generation],
                llm_output={
                    "model_name": self.model_name,
                    "provider": str(self.provider) if self.provider else None,
                },
            )
            
        except Exception as e:
            logger.error(f"Error in g4f async generation: {e}")
            raise

    @classmethod
    def get_lc_namespace(cls) -> list[str]:
        """Get the namespace of the langchain object."""
        return ["langchain", "chat_models", "g4f"]

    @property
    def lc_secrets(self) -> dict[str, str]:
        """Return secrets dict."""
        return {"api_key": "G4F_API_KEY"} if self.api_key else {}

    @property
    def lc_attributes(self) -> dict[str, Any]:
        """Return attributes dict."""
        attributes: dict[str, Any] = {}
        if self.provider:
            attributes["provider"] = str(self.provider)
        return attributes
