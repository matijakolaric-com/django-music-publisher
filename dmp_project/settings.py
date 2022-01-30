"""
Django settings for dmp_project project.
"""

import csv
import os
import dj_database_url
from decimal import Decimal

SOFTWARE = 'DMP.MATIJAKOLARIC.COM'
SOFTWARE_VERSION = '22.1 EXOFILE (OPEN SOURCE)'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', None)

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
    'django_cleanup',
    'rest_framework',
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

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

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

LOGIN_URL = '/login/'

DATA_UPLOAD_MAX_NUMBER_FIELDS = None

CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
SECURE_HSTS_SECONDS = 0 if DEBUG else 300
SECURE_HSTS_PRELOAD = not DEBUG
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = not DEBUG

# The name of the publisher. Use no comma in the name!
PUBLISHER_NAME = os.getenv('PUBLISHER', 'FREE MUSIC CATALOGUE SOFTWARE')

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
    os.getenv('PUBLISHING_AGREEMENT_PUBLISHER_PR', '0.5'))
PUBLISHING_AGREEMENT_PUBLISHER_MR = Decimal(
    os.getenv('PUBLISHING_AGREEMENT_PUBLISHER_MR', '1.0'))
PUBLISHING_AGREEMENT_PUBLISHER_SR = Decimal(
    os.getenv('PUBLISHING_AGREEMENT_PUBLISHER_SR', '1.0'))

# Set to one of the following options to change names and titles
# * 'upper' - changes all names and titles to UPPER CASE
# * 'title' - Changes all names to Title Case
# * 'smart' - Changes all UPPER CASE names and titles to Title Case
# Anything else makes no changes to names and titles
OPTION_FORCE_CASE = os.getenv('OPTION_FORCE_CASE')


# REMOTE FILES
# The default is Digital Ocean Spaces, but any S3 should work with AWS
# and any other S3. Support DMP by using the affiliation links below.
# For Digital Ocean (https://www.digitalocean.com/?refcode=b05ea0e8ec84), 
# you must set https://cloud.digitalocean.com/spaces/new?refcode=b05ea0e8ec84
# S3_BUCKET (name), S3_REGION (region code, fra1, lon3, etc.
# and https://cloud.digitalocean.com/account/api/tokens?refcode=b05ea0e8ec84
# S3_ID, S3 SECRET 

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID') or os.getenv('S3_ID')
AWS_SECRET_ACCESS_KEY = (
        os.getenv('AWS_SECRET_ACCESS_KEY') or
        os.getenv('S3_SECRET'))
AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME') or os.getenv('S3_REGION')
AWS_STORAGE_BUCKET_NAME = (
        os.getenv('AWS_STORAGE_BUCKET_NAME') or
        os.getenv('S3_BUCKET'))
AWS_S3_ENDPOINT_URL = (
        os.getenv('AWS_S3_ENDPOINT_URL') or
        f'https://{AWS_S3_REGION_NAME}.digitaloceanspaces.com')
AWS_QUERYSTRING_EXPIRE = os.getenv('AWS_QUERYSTRING_EXPIRE', 900)


S3_ENABLED = all([AWS_S3_REGION_NAME, AWS_STORAGE_BUCKET_NAME,
                  AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY])

OPTION_FILES = os.getenv('OPTION_FILES', S3_ENABLED)

if OPTION_FILES:
    if S3_ENABLED:
        # S3 media, use the bucket root
        DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    else:
        # normal file storage
        MEDIA_URL = os.getenv('MEDIA_URL', '/media/')
        MEDIA_ROOT = os.getenv('MEDIA_ROOT', os.path.join(BASE_DIR, 'media'))

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.BasicAuthentication',
    ]
}