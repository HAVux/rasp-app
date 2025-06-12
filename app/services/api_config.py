from os import environ
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_URL = environ.get("API_URL")

# API Endpoints
FOOD_API_URL = f"{BASE_URL}/food"
ORDER_API_URL = f"{BASE_URL}/order"
STATUS_API_URL = f"{ORDER_API_URL}/status"
