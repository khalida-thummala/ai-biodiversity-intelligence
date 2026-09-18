import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Explain in one sentence why soil organic carbon matters for biodiversity."
)
print("Response from Gemini 2.5 Flash:")
print(response.text)
