try:
    from bio_phil.shared_settings import *
except ImportError:
    pass

import os
from decouple import config

DEBUG = config('DEBUG', cast=bool)
basepath = '/kunden/homepages/41/d77006110/htdocs'
# STATIC_ROOT = basepath + 'BIOPHIL/BioPhil_Website/bio_phil/webapp/static'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

ALLOWED_HOSTS = ['bio-phil.net', 'bio-phil.herokuapp.com']
DEFAULT_DOMAIN = 'https://{}'.format(ALLOWED_HOSTS[0])

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
X_FRAME_OPTIONS = 'DENY'
SECURE_SSL_REDIRECT = True

SECURE_BROWSER_XSS_FILTER = True

SECURE_CONTENT_TYPE_NOSNIFF =  True

SECURE_HSTS_SECONDS = True

SECURE_HSTS_INCLUDE_SUBDOMAINS = True

SECURE_HSTS_PRELOAD = True

# INSTALLED_APPS = [
#     'webapp.apps.WebappConfig',
#     'background_task',
#     'django.contrib.admin',
#     'django.contrib.auth',
#     'django.contrib.contenttypes',
#     'django.contrib.sessions',
#     'django.contrib.messages',
#     # 'collectfast',
#     'django.contrib.staticfiles',
#     'storages',
#     'cloudinary_storage',
#     'cloudinary',
# ]

# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
#     },
#     'collectfast': {
#         'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
#         'LOCATION': 'collectfast_cache',
#         'TIMEOUT': 60,
#         'OPTIONS': {
#             'MAX_ENTRIES': 10000
#         },
#     },
# }
# COLLECTFAST_CACHE = 'collectfast'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/
