import os
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.environ.get("DB_PATH", "database.db")

CURRENCY_API_KEY = os.environ.get("CURRENCY_API_KEY", "")
CURRENCY_API_URL = os.environ.get("CURRENCY_API_URL", "https://api.freecurrencyapi.com/v1/latest")
CURRENCY_API_TIMEOUT = int(os.environ.get("CURRENCY_API_TIMEOUT", 10))

LOG_LEVEL = os.environ.get("LOG_LEVEL", "DEBUG")
LOG_DIR = os.environ.get("LOG_DIR", "./logs")
LOG_BASE_NAME = os.environ.get("LOG_BASE_NAME", "crossbank")

ALLOWED_ACCOUNT_TYPES = {"debit", "credit"}
ALLOWED_ACCOUNT_STATUS = {"platinum", "gold", "silver"}
ALLOWED_CURRENCIES = {"EUR", "USD", "UAH"}

if not CURRENCY_API_KEY:
    raise ValueError("CURRENCY_API_KEY must be set in your .env file or environment variables!")
