import os
from dotenv import load_dotenv
load_dotenv()

# ------- For Callbacks receive -->>
BACKEND_DATA_RECEIVE_DOMAIN= os.getenv("BACKEND_DATA_RECEIVE_DOMAIN", "http://localhost:8000")

# ---=== For Send Server Error to Discord ==>>
DISCORD_ERROR_WEBHOOK_URL = os.getenv("DISCORD_ERROR_WEBHOOK_URL", "")
SEND_ERRORS_TO_DISCORD = os.getenv("SEND_ERRORS_TO_DISCORD", "False").lower() in ['true', '1', 'yes']
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# ---- Stripe Configure (IF NEED)-->>
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

# ---- SSLCOMMERZ Configure (IF NEED)-->>
SSLCOMMERZ_STORE_ID = os.getenv("SSLCOMMERZ_STORE_ID", "")
SSLCOMMERZ_STORE_PASS = os.getenv("SSLCOMMERZ_STORE_PASS", "")
SSLCOMMERZ_IS_SANDBOX = os.getenv("SSLCOMMERZ_IS_SANDBOX", "True").lower() in ['true', '1', 'yes']