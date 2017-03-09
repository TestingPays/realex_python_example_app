from tp_python_realex_example.settings.base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY", "")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = []

REALEX_URL = os.environ.get("REALEX_URL", "https://api.realexpayments.com/epage-remote.cgi")
REALEX_VERIFY_SIGNED_URL = os.environ.get("REALEX_VERIFY_SIGNED_URL", "")
REALEX_VERIFY_ENROLLED_URL = os.environ.get("REALEX_VERIFY_ENROLLED_URL", "")
REALEX_CALLBACK_URL = os.environ.get("REALEX_CALLBACK_URL", "")
REALEX_MERCHANT_ID = os.environ.get("REALEX_MERCHANT_ID", "")
REALEX_SHARED_SECRET = os.environ.get("REALEX_SHARED_SECRET", "")

STATIC_URL = '/static/'

STATICFILES_DIRS = [os.path.join(BASE_DIR, "static"), ]
