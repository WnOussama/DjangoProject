from dotenv import load_dotenv
import os
load_dotenv()
from .celery import app as celery_app
__all__ = ('celery_app',)
env = os.getenv("DJANGO_SETTINGS_MODULE")


valid_settings = ["core.settings.production", "core.settings.local", "core.settings.development"]
if env not in valid_settings:
    raise ValueError(f"Invalid DJANGO_SETTINGS_MODULE: {env}. Must be one of {valid_settings}.")

print(f"==>> Usign settings: {env} <<==")

if env == "core.settings.production":
    from .settings.production import *
elif env == "core.settings.dev":
    from .settings.development import *
else:
    from .settings.local import *
