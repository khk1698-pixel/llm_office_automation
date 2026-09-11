import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

print("API KEY 확인:", api_key)  # 👈 이거 중요 (디버깅)

genai.configure(api_key=api_key)

for m in genai.list_models():
    print(m.name)