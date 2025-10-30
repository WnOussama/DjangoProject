import os

# --- For Google auth and Email -->>
GOGGLE_APP_PASSWORD=os.getenv("GOGGLE_APP_PASSWORD", "")
GOOGLE_CLIENT_ID=os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET=os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI=os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback/")
GOOGLE_SCOPE = os.getenv("GOOGLE_SCOPE", "https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile")

# --====>> OTHER SOCIAL MEDIA OAuth <<====---
PINTEREST_CLIENT_ID=os.getenv("PINTEREST_CLIENT_ID", "")
PINTEREST_CLIENT_SECRET = os.getenv("PINTEREST_CLIENT_SECRET", "")
PINTEREST_REDIRECT_URI = os.getenv("PINTEREST_REDIRECT_URI", "http://localhost:8000/auth/pinterest/callback/")

TIKTOK_CLIENT_KEY = os.getenv("TIKTOK_CLIENT_KEY", "")
TIKTOK_CLIENT_SECRET = os.getenv("TIKTOK_CLIENT_SECRET", "")
TIKTOK_REDIRECT_URI = os.getenv("TIKTOK_REDIRECT_URI", "http://localhost:8000/auth/tiktok/callback/")
TIKTOK_SCOPE = os.getenv("TIKTOK_SCOPE", "user.info.basic,user.info.email")
