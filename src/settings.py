from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(), verbose=True)
import os
API_URL=os.getenv("API_URL")
TELEGRAM_TOKEN=os.getenv("TELEGRAM_TOKEN")
