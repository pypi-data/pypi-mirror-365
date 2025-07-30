from abc import ABC, abstractmethod
from typing import Optional

class BaseProvider(ABC):
    """
    Abstract Base Class for all AI model providers.

    This class defines the standard interface that every provider-specific
    class (e.g., GeminiProvider, OpenAIProvider) must implement. This ensures
    that the main `generate` function in genai.py can interact with any
    provider in a consistent way.
    """

    def __init__(self, api_key: str):
        """
        Initializes the provider with the necessary API key.

        Args:
            api_key (str): The API key for the provider's service.
        """
        if not api_key or not isinstance(api_key, str):
            raise ValueError("A valid API key must be provided.")
        self.api_key = api_key
        self._initialize_client()

    @abstractmethod
    def _initialize_client(self):
        """
        An abstract method to initialize the provider-specific API client.
        
        Each subclass must implement this method to set up its specific client
        (e.g., `openai.OpenAI(api_key=self.api_key)`). This method is called
        by the base class's __init__ method.
        """
        pass

    @abstractmethod
    def generate(
        self,
        model: str,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 1.0,
        max_tokens: int = 2048,
        top_p: float = 1.0,
    ) -> str:
        """
        Generates a response from the provider's model.

        This is the core method that each provider subclass must implement
        according to its specific API requirements.

        Args:
            model (str): The specific model string for this provider (e.g., 'gpt-4o').
            prompt (str): The user's prompt.
            system_instruction (Optional[str]): System-level instructions.
            temperature (float): Controls randomness.
            max_tokens (int): Maximum length of the response.
            top_p (float): Nucleus sampling parameter.

        Returns:
            str: The generated text response from the model.
        
        Raises:
            NotImplementedError: If the subclass does not implement this method.
        """
        raise NotImplementedError(
            "Each provider must implement the 'generate' method."
        )