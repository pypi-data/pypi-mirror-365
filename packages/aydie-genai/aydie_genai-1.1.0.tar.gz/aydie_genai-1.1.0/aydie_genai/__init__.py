from aydie_genai.constants import VERSION

__version__ = VERSION

from . import genai

__all__ = [
    'genai',
]

print("aydie_genai package loaded successfully.")