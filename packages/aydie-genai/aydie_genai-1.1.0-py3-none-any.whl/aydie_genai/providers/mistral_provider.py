from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from mistralai.exceptions import MistralAPIException
from typing import Optional, List

from .base_provider import BaseProvider
from ..exceptions import AydieException

class MistralProvider(BaseProvider):
    """
    A provider class to handle interactions with MistralAI's models.

    This class implements the specific logic required to call the MistralAI API,
    including client initialization, parameter mapping, and response parsing.
    """

    def _initialize_client(self):
        """
        Initializes the MistralAI API client using the provided API key.
        """
        try:
            self.client = MistralClient(api_key=self.api_key)
        except Exception as e:
            raise AydieException(f"Failed to initialize MistralAI client: {e}")

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
        Generates a response from a MistralAI model.

        Args:
            model (str): The specific MistralAI model to use (e.g., 'mistral-large-latest').
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
        messages: List[ChatMessage] = []
        # Mistral handles system instructions as the first message in the chat history
        if system_instruction:
            messages.append(ChatMessage(role="system", content=system_instruction))
        messages.append(ChatMessage(role="user", content=prompt))

        try:
            response = self.client.chat(
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
                raise AydieException("Received a malformed response from MistralAI API.")

        except MistralAPIException as e:
            # Catch specific MistralAI API errors for better feedback
            raise AydieException(f"MistralAI API error: {e}")
        except Exception as e:
            # Catch any other potential errors
            raise AydieException(f"An unexpected error occurred while calling MistralAI API: {e}")
