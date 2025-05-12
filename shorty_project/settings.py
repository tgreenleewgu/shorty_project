from pathlib import Path
from decouple import config
import os


MONGODB_URI = config('MONGODB_URI')
GITHUB_CLIENT_ID = config('GITHUB_CLIENT_ID')
GITHUB_CLIENT_SECRET = config('GITHUB_CLIENT_SECRET')
SECRET_KEY = config('SECRET_KEY')
ENVIRONMENT = config('DJANGO_ENV', default='development')


# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables
ENVIRONMENT = config("DJANGO_ENV", default="development")
SECRET_KEY = config("SECRET_KEY", default="fallback-insecure-key")
DEBUG = ENVIRONMENT == "development"

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'rest_framework',
    'corsheaders',
    'allauth',
    'allauth.account',
    'rest_framework.authtoken',
    'dj_rest_auth',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.github',
    'allauth.socialaccount.providers.google',
    'url_shortener.apps.UrlShortenerConfig',
]

SITE_ID = 1

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'shorty_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'shorty_project.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

MONGODB_URI = config('MONGODB_URI', default='')

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
}

# REST Auth
REST_AUTH = {
    'USE_JWT': False,
    'JWT_AUTH_COOKIE': 'my-app-auth',
    'JWT_AUTH_REFRESH_COOKIE': 'my-refresh-token',
}

# Auth backends
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Social Providers
SOCIALACCOUNT_PROVIDERS = {
    'github': {
        'APP': {
            'client_id': os.environ.get("GITHUB_CLIENT_ID"),
            'secret': os.environ.get("GITHUB_CLIENT_SECRET"),
        },
        'SCOPE': ['user:email'],
        'AUTH_PARAMS': {'prompt': 'consent'}
    },
    'google': {
        'APP': {
            'client_id': os.environ.get("GOOGLE_CLIENT_ID"),
            'secret': os.environ.get("GOOGLE_CLIENT_SECRET"),
            'key': ''
        },
        "SCOPE": ["profile", "email"],
        "AUTH_PARAMS": {"access_type": "online"},
    }
}

ACCOUNT_USER_MODEL_USERNAME_FIELD = 'username'
ACCOUNT_LOGIN_METHODS = {
    'username': {
        'enabled': True,
        'verification': None
    }
}

SOCIALACCOUNT_LOGIN_ON_GET = True
SOCIALACCOUNT_AUTO_SIGNUP = True
ACCOUNT_UNIQUE_EMAIL = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True
SOCIALACCOUNT_EMAIL_VERIFICATION = "none"
SOCIALACCOUNT_QUERY_EMAIL = True

# Environment-specific settings
CORS_ALLOW_CREDENTIALS = True

if ENVIRONMENT == "production":
    ALLOWED_HOSTS = [
        '54.237.91.6',
        'www.getshortylinks.com',
        'getshortylinks.com',
        'api.getshortylinks.com',
	'127.0.0.1',
    ]
    CORS_ALLOWED_ORIGINS = [
        'https://www.getshortylinks.com',
        'https://getshortylinks.com',
    ]
    CORS_ALLOW_CREDENTIALS = True  

    CSRF_TRUSTED_ORIGINS = [
        'https://www.getshortylinks.com',
        'https://getshortylinks.com',
        'https://api.getshortylinks.com',
    ]
    LOGIN_REDIRECT_URL = 'https://www.getshortylinks.com/'
    ACCOUNT_LOGOUT_REDIRECT_URL = 'https://www.getshortylinks.com/'

    # Cookie settings
    SESSION_COOKIE_DOMAIN = ".getshortylinks.com"
    CSRF_COOKIE_DOMAIN = ".getshortylinks.com"
    SESSION_COOKIE_SAMESITE = "None"
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True


print(f"ENVIRONMENT={ENVIRONMENT}, DEBUG={DEBUG}")
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/tmp/django_debug.log',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'DEBUG',
    },
}

