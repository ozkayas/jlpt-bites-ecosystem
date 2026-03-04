from dotenv import load_dotenv; load_dotenv(); import os; print(len(os.environ.get('GEMINI_API_KEYS', '').split(',')))
