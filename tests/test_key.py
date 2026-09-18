import os
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
print(f"API key starts with: {api_key[:10]}... (length: {len(api_key)})")

import google.generativeai as genai

genai.configure(api_key=api_key)
# List available models
try:
    for m in genai.list_models():
        if "generateContent" in m.supported_generation_methods:
            print(f"Available model: {m.name}")
            break
except Exception as e:
    print(f"Error testing API: {e}")
