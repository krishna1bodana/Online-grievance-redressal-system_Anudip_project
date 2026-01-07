"""
Django settings for core project.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Then change your email settings to use these variables:
EMAIL_HOST_USER = os.getenv('EMAIL_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_PASS')
from pathlib import Path
import os

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent


# =========================
# SECURITY
# =========================

SECRET_KEY = os.getenv(
    'DJANGO_SECRET_KEY',
    'django-insecure-dev-key-change-in-production'
)

DEBUG = True

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
]


# =========================
# APPLICATIONS
# =========================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Custom App
    'grievance.apps.GrievanceConfig',
]


# =========================
# MIDDLEWARE
# =========================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # Must be after AuthMiddleware
    'grievance.middleware.RequireEmailMiddleware', 
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


ROOT_URLCONF = 'core.urls'


# =========================
# TEMPLATES
# =========================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # Custom Processor for Navbar Notifications
                'grievance.context_processors.notification_context',
            ],
        },
    },
]


WSGI_APPLICATION = 'core.wsgi.application'


# =========================
# DATABASE
# =========================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# =========================
# PASSWORD VALIDATION
# =========================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# =========================
# INTERNATIONALIZATION
# =========================

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True
USE_TZ = True


# =========================
# STATIC & MEDIA FILES
# =========================

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
# Directory where 'collectstatic' will put files for production
STATIC_ROOT = BASE_DIR / 'staticfiles' 

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# =========================
# AUTH REDIRECTS
# =========================

# Post-login logic handled by your custom view
LOGIN_REDIRECT_URL = 'grievance:post_login_redirect'
LOGOUT_REDIRECT_URL = 'login'


# =========================
# EMAIL CONFIGURATION
# =========================

# Console backend prints emails to your terminal/cmd
# =========================
# EMAIL CONFIGURATION (LIVE)
# =========================

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Gmail SMTP Settings
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# Your Credentials
EMAIL_HOST_USER = 'bodanakrishna38@gmail.com' 

# Use the 16-character App Password from Google
EMAIL_HOST_PASSWORD = 'fmelnwmztpvlevbi' 

# Branding
DEFAULT_FROM_EMAIL = 'Grievance Portal <bodanakrishna38@gmail.com>'

# =========================
# APP-SPECIFIC CONFIG
# =========================

ADMIN_EMAIL = 'bodanakrishna38@gmail.com'
NEWS_API_KEY = os.getenv('NEWS_API_KEY', 'your-fallback-key')
# =========================
# DEFAULT AUTO FIELD
# =========================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'