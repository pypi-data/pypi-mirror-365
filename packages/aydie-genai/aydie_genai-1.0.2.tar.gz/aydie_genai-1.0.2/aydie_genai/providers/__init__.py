# Import the base class and all specific provider implementations.
# This makes them available for import from the 'aydie_genai.providers' namespace.
from .base_provider import BaseProvider
from .gemini_provider import GeminiProvider
from .openai_provider import OpenAIProvider
from .claude_provider import ClaudeProvider
from .groq_provider import GroqProvider
from .deepseek_provider import DeepseekProvider
# from .mistral_provider import MistralProvider

# Define the public API for the 'providers' sub-package.
# When a user does `from aydie_genai.providers import *`, only these names
# will be imported. This helps prevent namespace pollution.
__all__ = [
    "BaseProvider",
    "GeminiProvider",
    "OpenAIProvider",
    "ClaudeProvider",
    "GroqProvider",
    "DeepseekProvider",
    "MistralProvider",
]
