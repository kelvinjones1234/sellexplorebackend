import os
from pathlib import Path
from datetime import timedelta
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file (using python-dotenv)

load_dotenv()


# Utility function to get environment variables
def get_env_variable(var_name, default=None):
    value = os.getenv(var_name, default)
    if value is None:
        raise ImproperlyConfigured(f"Set the {var_name} environment variable")
    return value


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_env_variable("DJANGO_SECRET_KEY")

# Environment-based settings
ENVIRONMENT = get_env_variable("DJANGO_ENV", "development")
DEBUG = ENVIRONMENT == "development"

# Allowed hosts
ALLOWED_HOSTS = get_env_variable("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(
    ","
)
if not DEBUG:
    ALLOWED_HOSTS.extend(["sellexplore.pythonanywhere.com", "*.sellexplore.shop"])

# Application definition
INSTALLED_APPS = [
    # Third-party apps
    "rest_framework",
    "corsheaders",
    "rest_framework_simplejwt",
    "django_filters",
    "storages",
    # Custom apps
    "account",
    "store_setting",
    "product",
    "detail",
    "public",
    # Default Django apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.http.ConditionalGetMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"

# Database configuration
if DEBUG:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": get_env_variable("DB_NAME"),
            "USER": get_env_variable("DB_USER"),
            "PASSWORD": get_env_variable("DB_PASSWORD"),
            "HOST": get_env_variable("DB_HOST"),
            "PORT": get_env_variable("DB_PORT", "3306"),
            "OPTIONS": {
                "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
            },
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"


# Media files
if DEBUG:
    MEDIA_URL = "/media/"
    MEDIA_ROOT = BASE_DIR / "media"
else:
    STORAGES = {
        "staticfiles": {
            "BACKEND": "helper.cloudflare.storages.StaticStorage",
            "OPTIONS": {
                "bucket_name": get_env_variable("CLOUDFLARE_R2_BUCKET"),
                "access_key": get_env_variable("CLOUDFLARE_R2_ACCESS_KEY"),
                "secret_key": get_env_variable("CLOUDFLARE_R2_SECRETE_KEY"),
                "endpoint_url": get_env_variable("CLOUDFLARE_R2_BUCKET_ENDPOINT"),
                "default_acl": "public-read",
                "signature_version": "s3v4",
            },
        },
        "default": {
            "BACKEND": "helper.cloudflare.storages.MediaStorage",
            "OPTIONS": {
                "bucket_name": get_env_variable("CLOUDFLARE_R2_BUCKET"),
                "access_key": get_env_variable("CLOUDFLARE_R2_ACCESS_KEY"),
                "secret_key": get_env_variable("CLOUDFLARE_R2_SECRETE_KEY"),
                "endpoint_url": get_env_variable("CLOUDFLARE_R2_BUCKET_ENDPOINT"),
                "default_acl": "public-read",
                "signature_version": "s3v4",
            },
        },
    }

# Custom user model
AUTH_USER_MODEL = "account.User"

# CORS settings
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:3000",
    "http://greenfarm.localhost:3000",
    "http://localhost:3000",
    "https://onlinestore-mauve.vercel.app",
    "https://sellexplore.shop",
]
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^http:\/\/.*\.localhost:3000$",
    r"^https:\/\/.*\.sellexplore\.shop$",
]

CORS_EXPOSE_HEADERS = [
    "ETag",
    "Last-Modified",
    "Cache-Control",
]

CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
    # Add these two headers for caching
    "if-modified-since",
    "if-none-match",
]


# Simple JWT settings
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": False,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": "",
    "AUDIENCE": None,
    "ISSUER": None,
    "JSON_ENCODER": None,
    "JWK_URL": None,
    "LEEWAY": 0,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",
    "JTI_CLAIM": "jti",
    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),
    "TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainPairSerializer",
    "TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSerializer",
    "TOKEN_VERIFY_SERIALIZER": "rest_framework_simplejwt.serializers.TokenVerifySerializer",
    "TOKEN_BLACKLIST_SERIALIZER": "rest_framework_simplejwt.serializers.TokenBlacklistSerializer",
    "SLIDING_TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainSlidingSerializer",
    "SLIDING_TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSlidingSerializer",
}

# REST Framework settings
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
}

# Paystack
PAYSTACK_SECRET_KEY = get_env_variable(
    "PAYSTACK_SECRET_KEY",
    "sk_test_53e9c70384f773cd7ff62bc130f435ef17f08657" if DEBUG else None,
)

# Email configuration
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = get_env_variable("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(get_env_variable("EMAIL_PORT", "465"))
EMAIL_USE_SSL = get_env_variable("EMAIL_USE_SSL", "True").lower() == "true"
EMAIL_USE_TLS = get_env_variable("EMAIL_USE_TLS", "False").lower() == "true"
EMAIL_HOST_USER = get_env_variable("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = get_env_variable("EMAIL_HOST_PASSWORD")

# Logging configuration
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple" if DEBUG else "verbose",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "logs" / "django.log",
            "formatter": "verbose",
            "level": "INFO",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"] if not DEBUG else ["console"],
            "level": "INFO",
            "propagate": True,
        },
        "myapp": {
            "handlers": ["console", "file"] if not DEBUG else ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# Ensure log directory exists
os.makedirs(BASE_DIR / "logs", exist_ok=True)
