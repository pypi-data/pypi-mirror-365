from typing import Optional, Dict, Any, Type

from .exceptions import AydieException, ModelNotSupportedError, APIKeyNotFoundError
from .utils import MODEL_PROVIDER_MAP, load_api_key

# Providers Imports
from .providers.base_provider import BaseProvider
from .providers.gemini_provider import GeminiProvider
from .providers.openai_provider import OpenAIProvider
from .providers.claude_provider import ClaudeProvider
from .providers.groq_provider import GroqProvider
from .providers.deepseek_provider import DeepseekProvider
# from .providers.mistral_provider import MistralProvider


# Provider Class Mapping
# This dictionary maps the provider name string from utils.py to the
# actual Python class that handles the logic for that provider.
PROVIDER_CLASSES: Dict[str, Type[BaseProvider]] = {
    "gemini": GeminiProvider,
    "openai": OpenAIProvider,
    "claude": ClaudeProvider,
    "groq": GroqProvider,
    "deepseek": DeepseekProvider,
    # "mistral": MistralProvider,
}


def generate(
    model: str,
    prompt: str,
    system_instruction: Optional[str] = None,
    temperature: float = 0.5,
    max_tokens: int = 2048,
    top_p: float = 1.0,
    api_key: Optional[str] = None,) -> str:
    """
    Generates a response from a specified generative AI model.

    This is the main entry point for the aydie_genai library. It provides a
    unified interface to interact with various large language models from
    different providers by abstracting away the provider-specific code.

    Args:
        model (str): The identifier for the model to use (e.g., 'gpt-4o', 
                     'gemini-1.5-pro', 'claude-3-opus-20240229'). See the 
                     documentation for a full list of supported models.
        prompt (str): The main user input, question, or instruction for the model.
        system_instruction (Optional[str], optional): A directive, context, or
            persona to guide the model's behavior throughout the conversation.
            Defaults to None.
        temperature (float, optional): Controls the randomness of the output. 
            Must be between 0.0 and 2.0. Lower values (e.g., 0.2) make the output
            more deterministic, while higher values (e.g., 1.5) make it more
            creative or random. Defaults to 1.0.
        max_tokens (int, optional): The maximum number of tokens (words or
            pieces of words) to generate in the response. Defaults to 2048.
        top_p (float, optional): Nucleus sampling. The model considers only the
            tokens with the highest probability mass that add up to top_p. It's an
            alternative to temperature. Defaults to 1.0.
        api_key (Optional[str], optional): Allows you to directly provide the API
            key for the model's provider. If not provided, the library will
            attempt to load it from the corresponding environment variable
            (e.g., 'OPENAI_API_KEY'). Defaults to None.

    Raises:
        ModelNotSupportedError: If the 'model' string is not recognized or
                                supported by the library.
        APIKeyNotFoundError: If the required API key for the model's provider
                             is not passed directly or found in the environment.
        AydieException: For general API errors, connection issues, or other
                        problems that occur during the generation process.

    Returns:
        str: The generated text response from the model.
    """
    # Look up the model in our central provider map
    model_info = MODEL_PROVIDER_MAP.get(model)
    if not model_info:
        raise ModelNotSupportedError(model_name=model)

    provider_name = model_info["provider"]
    api_key_var = model_info["api_key_var"]

    # Determine the API key to use (direct argument > environment variable)
    final_api_key = api_key or load_api_key(api_key_var)
    if not final_api_key:
        raise APIKeyNotFoundError(provider_name=provider_name, key_variable=api_key_var)

    # Select the appropriate provider class from our mapping
    provider_class = PROVIDER_CLASSES.get(provider_name)
    if not provider_class:
        # This is an internal library configuration error, not a user error.
        raise AydieException(f"Internal error: Provider '{provider_name}' is defined in maps but not implemented. Please update the module or try using a different version.")

    # Instantiate the provider and call its generate method
    try:
        # Create an instance of the chosen provider (e.g., OpenAIProvider)
        provider_instance = provider_class(api_key=final_api_key)
        
        # Delegate the generation task to the provider instance
        response = provider_instance.generate(
            model=model,
            prompt=prompt,
            system_instruction=system_instruction,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
        )
        return response
    
    except Exception as e:
        # Catch any exception from the provider's SDK (e.g., network error,
        # authentication error) and wrap it in our custom exception for a
        # consistent error-handling experience for the user.
        raise AydieException(f"An error occurred with the '{provider_name}' provider: {e}")