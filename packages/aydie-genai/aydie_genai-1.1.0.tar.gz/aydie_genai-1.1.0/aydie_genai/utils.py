import os
from dotenv import load_dotenv
from typing import Optional, Dict, Any

# Load environment variables from a .env file
load_dotenv()

# Model to Provider Mapping
# This dictionary is the single source of truth for which provider handles which model.
# It also maps the provider to the required environment variable for the API key.
MODEL_PROVIDER_MAP: Dict[str, Dict[str, Any]] = {
    # Google Gemini
    "gemini-1.5-pro-latest": {"provider": "gemini", "api_key_var": "GOOGLE_API_KEY"},
    "gemini-1.5-pro": {"provider": "gemini", "api_key_var": "GOOGLE_API_KEY"},
    "gemini-1.5-flash": {"provider": "gemini", "api_key_var": "GOOGLE_API_KEY"},
    "gemini-1.0-pro": {"provider": "gemini", "api_key_var": "GOOGLE_API_KEY"},
    "gemini-2.5-flash": {"provider": "gemini", "api_key_var": "GOOGLE_API_KEY"},
    "gemini-2.5-pro": {"provider": "gemini", "api_key_var": "GOOGLE_API_KEY"},
    
    # OpenAI
    "gpt-4o": {"provider": "openai", "api_key_var": "OPENAI_API_KEY"},
    "gpt-4-turbo": {"provider": "openai", "api_key_var": "OPENAI_API_KEY"},
    "gpt-3.5-turbo": {"provider": "openai", "api_key_var": "OPENAI_API_KEY"},
    "gpt-4.1": {"provider": "openai", "api_key_var": "OPENAI_API_KEY"},
    "gpt-4.1-mini": {"provider": "openai", "api_key_var": "OPENAI_API_KEY"},

    # Anthropic Claude
    "claude-3-opus-20240229": {"provider": "claude", "api_key_var": "ANTHROPIC_API_KEY"},
    "claude-3-sonnet-20240229": {"provider": "claude", "api_key_var": "ANTHROPIC_API_KEY"},
    "claude-3-haiku-20240307": {"provider": "claude", "api_key_var": "ANTHROPIC_API_KEY"},
    "claude-3.5-sonnet": {"provider": "claude", "api_key_var": "ANTHROPIC_API_KEY"},

    # Groq
    "llama3-70b-8192": {"provider": "groq", "api_key_var": "GROQ_API_KEY"},
    "llama3-8b-8192": {"provider": "groq", "api_key_var": "GROQ_API_KEY"},
    "mixtral-8x7b-32768": {"provider": "groq", "api_key_var": "GROQ_API_KEY"},
    "llama3-70b-131k": {"provider": "groq", "api_key_var": "GROQ_API_KEY"},

    # DeepSeek
    "deepseek-chat": {"provider": "deepseek", "api_key_var": "DEEPSEEK_API_KEY"},
    "deepseek-coder": {"provider": "deepseek", "api_key_var": "DEEPSEEK_API_KEY"},
    "deepseek-v2-chat": {"provider": "deepseek", "api_key_var": "DEEPSEEK_API_KEY"},

    # MistralAI
    "mistral-large-latest": {"provider": "mistral", "api_key_var": "MISTRAL_API_KEY"},
    "mistral-small-latest": {"provider": "mistral", "api_key_var": "MISTRAL_API_KEY"},
    "open-mixtral-8x7b": {"provider": "mistral", "api_key_var": "MISTRAL_API_KEY"},
    "mistral-medium-latest": {"provider": "mistral", "api_key_var": "MISTRAL_API_KEY"},
}


def load_api_key(key_variable: str) -> Optional[str]:
    """
    Loads an API key from the environment variables.

    This function first ensures that variables from a potential .env file
    are loaded, and then attempts to retrieve the specified key.

    Args:
        key_variable (str): The name of the environment variable
                            (e.g., 'OPENAI_API_KEY').

    Returns:
        Optional[str]: The API key if found, otherwise None.
    """
    api_key = os.getenv(key_variable)
    return api_key