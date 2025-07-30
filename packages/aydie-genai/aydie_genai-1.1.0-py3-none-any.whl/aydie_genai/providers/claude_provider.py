import anthropic
from typing import Optional, List, Dict, Any

from .base_provider import BaseProvider
from ..exceptions import AydieException

class ClaudeProvider(BaseProvider):
    """
    A provider class to handle interactions with Anthropic's Claude models.

    This class implements the specific logic required to call the Claude API,
    including client initialization, parameter mapping, and response parsing.
    """

    def _initialize_client(self):
        """
        Initializes the Anthropic API client using the provided API key.
        """
        try:
            self.client = anthropic.Anthropic(api_key=self.api_key)
        except Exception as e:
            raise AydieException(f"Failed to initialize Anthropic client: {e}")

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
        Generates a response from a Claude model.

        Args:
            model (str): The specific Claude model to use (e.g., 'claude-3-opus-20240229').
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
        # The Anthropic API requires the prompt to be in a 'messages' list.
        messages: List[Dict[str, Any]] = [{"role": "user", "content": prompt}]

        try:
            # The 'system' parameter is a dedicated field in the Claude API
            response = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_instruction, # Pass system instruction here
                messages=messages,
                top_p=top_p,
            )

            # Extract the text content from the response object.
            # The response content is a list, we typically want the first text block.
            if response.content and isinstance(response.content, list) and hasattr(response.content[0], 'text'):
                return response.content[0].text
            else:
                raise AydieException("Received a malformed response from Claude API.")

        except anthropic.APIError as e:
            # Catch specific Anthropic API errors for better feedback
            raise AydieException(f"Claude API error: {e}")
        except Exception as e:
            # Catch any other potential errors
            raise AydieException(f"An unexpected error occurred while calling Claude API: {e}")