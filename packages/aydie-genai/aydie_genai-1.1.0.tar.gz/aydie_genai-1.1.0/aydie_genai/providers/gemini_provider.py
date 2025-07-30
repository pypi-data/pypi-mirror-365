import google.generativeai as genai
from typing import Optional

from .base_provider import BaseProvider
from ..exceptions import AydieException

class GeminiProvider(BaseProvider):
    """
    A provider class to handle interactions with Google's Gemini models.

    This class implements the specific logic required to call the Gemini API,
    including client initialization, parameter mapping, and response parsing.
    """

    def _initialize_client(self):
        """
        Configures the Google Generative AI client with the provided API key.
        """
        try:
            genai.configure(api_key=self.api_key)
        except Exception as e:
            raise AydieException(f"Failed to configure Google Gemini client: {e}")

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
        Generates a response from a Gemini model.

        Args:
            model (str): The specific Gemini model to use (e.g., 'gemini-1.5-pro').
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
        try:
            # Initialize the specific model with the system instruction
            generative_model = genai.GenerativeModel(
                model_name=model,
                system_instruction=system_instruction
            )

            # Create the generation configuration, mapping our standard names
            # to the names required by the Gemini API.
            generation_config = genai.types.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p
            )

            # Generate the content
            response = generative_model.generate_content(
                prompt,
                generation_config=generation_config
            )

            # Extract the text from the response.
            # The response might not have text if it was blocked.
            if response.text:
                return response.text
            elif response.prompt_feedback and response.prompt_feedback.block_reason:
                raise AydieException(f"Request was blocked by Gemini API. Reason: {response.prompt_feedback.block_reason.name}")
            else:
                 raise AydieException("Received an empty or malformed response from Gemini API.")

        except Exception as e:
            # Catch any other potential errors from the Google library
            raise AydieException(f"An unexpected error occurred while calling Gemini API: {e}")