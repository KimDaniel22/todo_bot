import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TELEGRAM_TOKEN')
ENVIRONMENT = os.getenv('ENVIRONMENT', 'PROD')