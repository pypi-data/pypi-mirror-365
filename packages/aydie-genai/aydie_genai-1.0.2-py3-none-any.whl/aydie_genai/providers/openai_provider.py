import openai
from typing import Optional, List, Dict, Any

from .base_provider import BaseProvider
from ..exceptions import AydieException

class OpenAIProvider(BaseProvider):
    """
    A provider class to handle interactions with OpenAI's models (e.g., GPT-4, GPT-3.5).

    This class implements the specific logic required to call the OpenAI API,
    including client initialization, parameter mapping, and response parsing.
    """

    def _initialize_client(self):
        """
        Initializes the OpenAI API client using the provided API key.
        """
        try:
            self.client = openai.OpenAI(api_key=self.api_key)
        except Exception as e:
            raise AydieException(f"Failed to initialize OpenAI client: {e}")

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
        Generates a response from an OpenAI model.

        Args:
            model (str): The specific OpenAI model to use (e.g., 'gpt-4o').
            prompt (str): The user's prompt.
            system_instruction (Optional[str]): System-level instructions for the model.
            temperature (float): Controls randomness of the output.
            max_tokens (int): Maximum length of the response.
            top_p (float): Nucleus sampling parameter.

        Returns:
            str: The generated text response from the model.
        
        Raises:
            AydieException: If the API call fails or the response is malformed.
        """
        # The OpenAI API expects messages in a specific list format.
        messages: List[Dict[str, str]] = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
            )

            # Extract the text content from the response object.
            if response.choices and response.choices[0].message:
                return response.choices[0].message.content or ""
            else:
                raise AydieException("Received a malformed response from OpenAI API.")

        except openai.APIError as e:
            # Catch specific OpenAI API errors for better feedback
            raise AydieException(f"OpenAI API error: {e}")
        except Exception as e:
            # Catch any other potential errors
            raise AydieException(f"An unexpected error occurred while calling OpenAI API: {e}")