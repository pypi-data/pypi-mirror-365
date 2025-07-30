from aydie_genai import genai
import dotenv
import os

dotenv.load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

response = genai.generate(model="gemini-2.5-flash",
                          prompt="I need to by new iPhone.",
                          system_instruction="You are AI agent who works for Apple Customer Support",
                          api_key = GEMINI_API_KEY,
                          max_tokens=1024)

print(response)