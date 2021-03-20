"""
Django settings for dmp_project project.
"""

import csv
import os
import dj_database_url
from django.core.management.utils import get_random_secret_key
from decimal import Decimal

SOFTWARE = 'DMP.MATIJAKOLARIC.COM'
SOFTWARE_VERSION = '21.1 VICTOR (OPEN SOURCE)'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', get_random_secret_key())

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', False)

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(',')

INSTALLED_APPS = [
    'music_publisher.apps.MusicPublisherConfig',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'dmp_project.urls'

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

WSGI_APPLICATION = 'dmp_project.wsgi.application'

DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///{}'.format(os.path.join(BASE_DIR, 'db.sqlite3')))}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = os.getenv('STATIC_URL', '/static/')

STATIC_ROOT = os.getenv('STATIC_ROOT', os.path.join(BASE_DIR, 'static'))

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "dmp_project", "static"),
]

TIME_INPUT_FORMATS = [
    '%H:%M:%S',     # '14:30:59'
    '%M:%S',        # '14:30'
]

path = os.path.join(BASE_DIR, 'music_publisher', 'societies.csv')

with open(path, 'r') as f:
    reader = csv.reader(f)
    SOCIETIES = sorted(
        ((str(row[0]), '{} ({})'.format(row[1], row[2]))
         for row in reader),
        key=lambda row: row[1])

LOGIN_URL = '/login/'

DATA_UPLOAD_MAX_NUMBER_FIELDS = None

CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
SECURE_HSTS_SECONDS = 0 if DEBUG else 300
SECURE_HSTS_PRELOAD = not DEBUG
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = not DEBUG

# The name of the publisher. Use no comma in the name!
PUBLISHER_NAME = os.getenv('PUBLISHER', 'DJANGO-MUSIC-PUBLISHER')

# CWR Delivery code, issued by collecting societies
PUBLISHER_CODE = os.getenv('PUBLISHER_CODE', '')

# IPI Name # is required, issued by collecting societies
PUBLISHER_IPI_NAME = os.getenv('PUBLISHER_IPI_NAME', '')
# IPI Base # is rarely used, issued by collecting societies
PUBLISHER_IPI_BASE = os.getenv('PUBLISHER_IPI_BASE', None)

# Affiliation societies for performance, mechanical and sync rights
# Numerical value as string without the leading zero:
# '52' for PRS, '44' for MCPS, '10' for ASCAP, '34' for HFA. etc.
# see  music_publisher/societies.csv
PUBLISHER_SOCIETY_PR = os.getenv('PUBLISHER_SOCIETY_PR', None)
PUBLISHER_SOCIETY_MR = os.getenv('PUBLISHER_SOCIETY_MR', None)
PUBLISHER_SOCIETY_SR = os.getenv('PUBLISHER_SOCIETY_SR', None)

# Shares transferred to the original publisher, default to 50%/100%/100%
PUBLISHING_AGREEMENT_PUBLISHER_PR = Decimal(
    os.getenv(
        'PUBLISHING_AGREEMENT_PUBLISHER_PR',
        os.getenv('PUBLISHER_AGREEMENT_PR', '0.5')))
PUBLISHING_AGREEMENT_PUBLISHER_MR = Decimal(
    os.getenv('PUBLISHING_AGREEMENT_PUBLISHER_MR', '1.0'))
PUBLISHING_AGREEMENT_PUBLISHER_SR = Decimal(
    os.getenv('PUBLISHING_AGREEMENT_PUBLISHER_SR', '1.0'))

# Set to True for societies that require society-assigned agreement numbers
# PRS/MCPS, BUMA/STEMRA, Scandinavian societies.
REQUIRE_SAAN = os.getenv('REQUIRE_SAAN', False)

# Set to True if you have a standard publishing agreement with writers
REQUIRE_PUBLISHER_FEE = os.getenv('REQUIRE_PUBLISHER_FEE', False)

ENABLE_NOTES = os.getenv('ENABLE_NOTES', False)
FORCE_CASE = os.getenv('FORCE_CASE')
