try:
    from bio_phil.shared_settings import *
except ImportError:
    pass

# ---------- REMOVE/CHANGE IN PRODUCTION ----------
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_DOMAIN = 'localhost:8000'