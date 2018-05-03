

from dotenv import load_dotenv

from pathlib import Path  # python3 only
env_path = Path('.') / '.env'
load_dotenv(verbose=True, dotenv_path=env_path)
import os
API_URL=os.getenv("API_URL")
TELEGRAM_TOKEN=os.getenv("TELEGRAM_TOKEN")
