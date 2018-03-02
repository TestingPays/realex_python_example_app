from tp_python_realex_example.settings.base import *
import dj_database_url

# Use a postgres DB
db_url = os.environ.get("DATABASE_URL")
if db_url:
    DATABASES['default'] = dj_database_url.parse(db_url, conn_max_age=600)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY", "mq(v8&i$ua(a&_@@$kd*7dglot32bbs7#nu*o77g^88+q(wpv3")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['realex-3d-secure-example.herokuapp.com']

TESTINGPAYS_API_KEY = os.environ.get("TP_API_KEY")

REALEX_URL = "https://api.testingpays.com/{0}/realex/v1/auth".format(TESTINGPAYS_API_KEY)

REALEX_VERIFY_SIGNED_URL = os.environ.get("REALEX_VERIFY_SIGNED_URL",
                                            "https://api.testingpays.com/{0}/realex/v1/3ds_verifysig".format(TESTINGPAYS_API_KEY))

REALEX_VERIFY_ENROLLED_URL = os.environ.get("REALEX_VERIFY_ENROLLED_URL",
                                            "https://api.testingpays.com/{0}/realex/v1/3ds_verifyenrolled".format(TESTINGPAYS_API_KEY))

REALEX_CALLBACK_URL = os.environ.get("REALEX_CALLBACK_URL",
                                            "http://127.0.0.1:8888/threedsverifysig")

REALEX_MERCHANT_ID = os.environ.get("REALEX_MERCHANT_ID",
                                            TESTINGPAYS_API_KEY)

REALEX_SHARED_SECRET = os.environ.get("REALEX_SHARED_SECRET",
                                            "my_realex_shared_key") #Note you can use any string here when testing against testing pays

STATIC_URL = '/static/'

STATICFILES_DIRS = [os.path.join(BASE_DIR, "static"), ]
