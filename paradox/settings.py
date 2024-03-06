from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-ky158hdvh4uu6t4nlr^2l6j)n)rg1resuhv5+vna+l8v9^jpwh'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    "*"
]


# Application definition

INSTALLED_APPS = [
    'rest_framework',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'oauth2_provider',
    'social_django',
    'drf_social_oauth2',
    'corsheaders',
    'core',
    'frb',
    'finance',
    'fest',
    'utils',
]


REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.FormParser'
    ]
}


# SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = "207905362507-gv72ti9pr7gsc417r748kn4inamtd5ap.apps.googleusercontent.com"
# SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = "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"

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = "449424611527-h1qjsuq4b726156viv6q3ulkr0aq52de.apps.googleusercontent.com"
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = "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"

# VAR = "http://localhost:8000"

AUTHENTICATION_BACKENDS = (
    'drf_social_oauth2.backends.GoogleIdentityBackend',
    'drf_social_oauth2.backends.DjangoOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = [
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'openid'
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'paradox.coop_middleware.COOPMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'paradox.blacklist_middleware.BlacklistMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'paradox.urls'
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_WHITELIST = [
    'http://localhost:3000',
    'http://localhost:8000',
    'http://localhost:8080',
    'https://iitmparadox.org',
]


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
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',

            ],
        },
    },
]

WSGI_APPLICATION = 'paradox.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# setup for postgres

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres.joowioorsrxzhehsotiu',
        'PASSWORD': 'KA0piH3GsJM9QUfS',
        'HOST': 'aws-0-ap-south-1.pooler.supabase.com',
        'PORT': '5432'
    }
}
# DATABASES = {
#     'default': {
#         'ENGINE': 'django_cockroachdb',
#         'NAME': 'defaultdb',
#         'USER': 'paradox',
#         'PASSWORD': 'V-9G0gVDirfcVAUg2Z9m-g',
#         'HOST': 'paradox-24-3919.7s5.aws-ap-south-1.cockroachlabs.cloud',
#         'PORT': '26257',
#         'OPTIONS': {
#             'sslmode': 'verify-full',
#             'sslrootcert': 'root.crt'
#         },
#     },
# }
# TcNuAatJTNvxRLkYecIhHF88kLVJcY2DmMZGzSzN
# GNQ6pAA4FAVYlvswYgPqjspbXpOse79w6wBDnk6qQmSJEkwSRXtTptNgEHuqORs4GxLwfnUfEaAKS3oMjtpCRyQI2N4E5ApkytMf7xf3AJk4tLLcpVOVZ23b3QzhHzF9


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = "Asia/Kolkata"

# TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

# STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field
STATIC_ROOT = '/static/'
STATIC_URL = "https://paradox-central.s3.ap-south-1.amazonaws.com/"

AWS_ACCESS_KEY_ID = "AKIAU255DJ3NOYRL6777"
AWS_SECRET_ACCESS_KEY = "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"

AWS_STORAGE_BUCKET_NAME = "paradox-central"
AWS_S3_REGION_NAME = "ap-south-1"

AWS_DEFAULT_ACL = "public-read"
AWS_QUERYSTRING_AUTH = False


STORAGES = {
    "default": {"BACKEND": "storages.backends.s3.S3Storage"},
    "staticfiles": {"BACKEND": "storages.backends.s3.S3Storage"}
}
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_HOST_USER = 'noreply@iitmparadox.org'
# EMAIL_HOST_PASSWORD = 'qcfflqimdnyofera'
EMAIL_HOST = 'smtp.office365.com'
EMAIL_HOST_USER = 'noreply@mail.iitmparadox.org'
EMAIL_HOST_PASSWORD = 'Jog17172'
EMAIL_PORT = 587
