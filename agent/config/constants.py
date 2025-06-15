import os

PROVIDER = os.getenv('MODEL_PROVIDER', 'google_genai')
MODEL_NAME = os.getenv('MODEL_NAME', 'gemini-2.0-flash')
MAX_OUTPUT_TOKENS= int(os.getenv('MAX_OUTPUT_TOKENS', 8192))
