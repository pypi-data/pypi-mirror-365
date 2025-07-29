import logging
from functools import wraps
from typing import Any, Callable

from ..base import Integration

logger = logging.getLogger(__name__)


class LiveKitIntegration(Integration):
    """Integration for LiveKit Agents framework."""
    
    PACKAGE_NAME = "livekit.plugins.openai"

    def setup(self) -> None:
        """Set up the LiveKit integration by patching LiveKit's OpenAI plugin."""
        try:
            # Import LiveKit's OpenAI plugin
            from livekit.plugins import openai as livekit_openai
            
            # Patch the LLM class constructor
            if hasattr(livekit_openai, 'LLM'):
                self._patch_method(
                    livekit_openai.LLM,
                    "__init__",
                    self._wrap_livekit_llm_init
                )
                logger.debug("Successfully patched LiveKit OpenAI LLM")
                
            # Patch the realtime model if it exists  
            if hasattr(livekit_openai, 'realtime') and hasattr(livekit_openai.realtime, 'RealtimeModel'):
                self._patch_method(
                    livekit_openai.realtime.RealtimeModel,
                    "__init__",
                    self._wrap_livekit_realtime_init
                )
                logger.debug("Successfully patched LiveKit OpenAI RealtimeModel")
                
        except ImportError:
            logger.debug("LiveKit OpenAI plugin not found, skipping integration")
        except Exception as e:
            logger.warning(f"Failed to setup LiveKit integration: {e}")

    def _wrap_livekit_llm_init(self, original: Callable) -> Callable:
        """Wrap LiveKit's LLM __init__ to instrument its methods."""
        @wraps(original)
        def wrapper(instance, *args: Any, **kwargs: Any) -> Any:
            # Call original init
            result = original(instance, *args, **kwargs)
            
            # Extract model name from kwargs
            model = kwargs.get('model', 'unknown')
            
            # Patch the chat method if it exists
            if hasattr(instance, 'chat'):
                self._patch_method(
                    instance,
                    'chat',
                    lambda orig: self._wrap_livekit_chat(orig, model)
                )
                
            return result
        return wrapper

    def _wrap_livekit_realtime_init(self, original: Callable) -> Callable:
        """Wrap LiveKit's RealtimeModel __init__ to instrument its methods."""
        @wraps(original)
        def wrapper(instance, *args: Any, **kwargs: Any) -> Any:
            # Call original init
            result = original(instance, *args, **kwargs)
            
            # Patch relevant methods
            # TODO: Add specific realtime model instrumentation as needed
            
            return result
        return wrapper

    def _wrap_livekit_chat(self, original: Callable, model: str) -> Callable:
        """Wrap LiveKit's chat method to trace LLM calls."""
        @wraps(original)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Start a span for the chat operation
            span = self.tracer.start_span(
                name="livekit.openai.chat",
                attributes={
                    "service.name": "livekit",
                    "kind": "llm",
                    "provider": "openai",
                    "model": model,
                    "integration": "livekit",
                    "streaming": kwargs.get("stream", False),
                },
                tags={"integration": "livekit", "llm_provider": "openai"},
            )
            
            try:
                # Extract messages if available
                messages = kwargs.get("messages", [])
                if messages and hasattr(messages[0], "content"):
                    span.set_attribute("messages", [{"role": m.role, "content": m.content} for m in messages])
                
                # Call original method
                result = await original(*args, **kwargs)
                
                # Try to capture response
                if hasattr(result, "choices") and result.choices:
                    first_choice = result.choices[0]
                    if hasattr(first_choice, "message"):
                        span.set_attribute("response", first_choice.message.content)
                
                return result
                
            except Exception as e:
                span.set_attribute("error", str(e))
                span.set_status("ERROR")
                raise
            finally:
                span.end()
                
        return wrapper

    def teardown(self) -> None:
        """Clean up the LiveKit integration."""
        # LiveKit integration cleanup if needed
        pass 