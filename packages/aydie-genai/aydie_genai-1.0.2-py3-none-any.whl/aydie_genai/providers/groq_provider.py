import openai
from typing import Optional, List, Dict, Any

from .base_provider import BaseProvider
from ..exceptions import AydieException

class GroqProvider(BaseProvider):
    """
    A provider class to handle interactions with Groq's high-speed models.

    This class leverages the OpenAI-compatible API provided by Groq, by pointing
    the OpenAI client to the correct base URL for Groq's service.
    """

    GROQ_API_BASE_URL = "https://api.groq.com/openai/v1"

    def _initialize_client(self):
        """
        Initializes the OpenAI-compatible client for the Groq API.
        """
        try:
            # We use the openai library but configure it for Groq's endpoint.
            self.client = openai.OpenAI(
                api_key=self.api_key,
                base_url=self.GROQ_API_BASE_URL
            )
        except Exception as e:
            raise AydieException(f"Failed to initialize Groq client: {e}")

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
        Generates a response from a Groq-hosted model (e.g., Llama, Mixtral).

        Args:
            model (str): The specific model to use (e.g., 'llama3-70b-8192').
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
                raise AydieException("Received a malformed response from Groq API.")

        except openai.APIError as e:
            # Catch specific API errors for better feedback
            raise AydieException(f"Groq API error: {e}")
        except Exception as e:
            # Catch any other potential errors
            raise AydieException(f"An unexpected error occurred while calling Groq API: {e}")