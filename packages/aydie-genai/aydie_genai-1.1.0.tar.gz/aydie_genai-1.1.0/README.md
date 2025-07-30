# aydie_genai

<p align="center">
  <img src="https://aydie.in/banner.jpg" alt="aydie_genai Banner" width="700">
</p>

<p align="center">
  <h3><strong>A simple, unified, and powerful Python library for generative AI.</strong></h3>
</p>

<p align="center">
    <a href="https://github.com/aydie/aydie_genai/blob/main/LICENSE"><img src="https://img.shields.io/pypi/l/aydie-genai.svg?style=for-the-badge&color=lightgrey" alt="License"></a>
</p>

---

`aydie_genai` is a Python library designed to eliminate the complexity of working with multiple Generative AI models. Instead of writing different code for Gemini, OpenAI, Claude, Groq, and others, you can use one simple, unified function to access them all.

## Key Features

- **Unified Interface**: A single `generate()` function for all supported models.
- **Simple & Intuitive**: Get started in minutes. No need to learn multiple SDKs.
- **Provider Agnostic**: Switch between models like `gpt-4o` and `gemini-1.5-pro` by changing a single string.
- **Built-in Documentation**: Rich docstrings provide in-console help via `help(genai.generate)`.
- **Robust Error Handling**: Custom exceptions for common issues like missing API keys.

## Supported Models

| Provider      | Supported Models                                                                                                                               | Environment Variable  |
|---------------|------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------|
| **Google** | `gemini-1.5-pro`, `gemini-1.5-flash`, `gemini-1.0-pro`, `gemini-2.5-pro`, `gemini-2.5-flash`                                                      | `GOOGLE_API_KEY`      |
| **OpenAI** | `gpt-4o`, `gpt-4-turbo`, `gpt-3.5-turbo`, `gpt-4.1`, `gpt-4.1-mini`                                                                              | `OPENAI_API_KEY`      |
| **Anthropic** | `claude-3-opus-20240229`, `claude-3-sonnet-20240229`, `claude-3-haiku-20240307`, `claude-3.5-sonnet`                                              | `ANTHROPIC_API_KEY`   |
| **Groq** | `llama3-70b-8192`, `llama3-8b-8192`, `mixtral-8x7b-32768`, `llama3-70b-131k`                                                                      | `GROQ_API_KEY`        |
| **DeepSeek** | `deepseek-chat`, `deepseek-coder`, `deepseek-v2-chat`                                                                                            | `DEEPSEEK_API_KEY`    |

## Installation

Install `aydie_genai` directly from PyPI:

```bash
pip install aydie-genai
```

## ⚡ Quick Start

### 1. Set Up Your API Keys

The library loads API keys from environment variables. The easiest way to manage these is to create a `.env` file in your project's root directory:

```ini
# .env file
GOOGLE_API_KEY="your_google_api_key"
OPENAI_API_KEY="your_openai_api_key"
ANTHROPIC_API_KEY="your_anthropic_api_key"
GROQ_API_KEY="your_groq_api_key"
DEEPSEEK_API_KEY="your_deepseek_api_key"
```

### 2. Generate a Response

Using the library is incredibly simple. Just import `genai` and call the `generate` function.

```python
from aydie_genai import genai

# Example 1: Using Google Gemini
response_gemini = genai.generate(
    model='gemini-1.5-pro',
    prompt='Explain the theory of relativity in simple terms for a five-year-old.',
    system_instruction='You are a friendly and patient teacher.'
)
print("Gemini says:", response_gemini)

# Example 2: Switching to OpenAI's GPT-4o is as easy as changing the model name
response_openai = genai.generate(
    model='gpt-4o',
    prompt='Write a short story about a robot who discovers music.'
)
print("\nOpenAI says:", response_openai)
```

## Function Parameters

The `genai.generate()` function accepts the following parameters:

| Parameter            | Type    | Description                                                                                             |
|----------------------|---------|---------------------------------------------------------------------------------------------------------|
| `model`              | `str`   | **Required**. The identifier for the model you want to use (e.g., `'gpt-4o'`).                          |
| `prompt`             | `str`   | **Required**. The main user input or question for the model.                                            |
| `system_instruction` | `str`   | A directive to guide the model's behavior or personality.                                               |
| `temperature`        | `float` | Controls randomness (0.0 for deterministic, 2.0 for random). Defaults to `1.0`.                         |
| `max_tokens`         | `int`   | The maximum number of tokens to generate in the response. Defaults to `2048`.                           |
| `top_p`              | `float` | Nucleus sampling parameter. Defaults to `1.0`.                                                          |
| `api_key`            | `str`   | Directly pass an API key, overriding the environment variable. Defaults to `None`.                      |

## Contributing

Contributions are welcome! Whether it's adding new models, improving documentation, or fixing bugs, your help is appreciated. Please feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Connect with Me

<p align="center">
  <a href="https://aydie.in" target="_blank"><img src="https://img.shields.io/badge/Website-aydie.in-blue?logo=googlechrome" alt="Website"></a>
  <a href="https://www.linkedin.com/in/aydiemusic" target="_blank"><img src="https://img.shields.io/badge/LinkedIn-Profile-blue?logo=linkedin" alt="LinkedIn"></a>
  <a href="https://x.com/aydiemusic" target="_blank"><img src="https://img.shields.io/badge/X-Twitter-black?logo=x" alt="Twitter"></a>
  <a href="https://instagram.com/aydiemusic" target="_blank"><img src="https://img.shields.io/badge/Instagram-Profile-e4405f?logo=instagram" alt="Instagram"></a>
  <a href="https://youtube.com/@aydiemusic" target="_blank"><img src="https://img.shields.io/badge/YouTube-Channel-ff0000?logo=youtube" alt="YouTube"></a>
  <a href="https://gitlab.com/aydie" target="_blank"><img src="https://img.shields.io/badge/GitLab-Profile-fca121?logo=gitlab" alt="GitLab"></a>
  <a href="mailto:business@aydie.in"><img src="https://img.shields.io/badge/Email-business@aydie.in-lightgrey?logo=gmail" alt="Email"></a>
</p>