"""
Django settings for graffitisWeb project.

Generated by 'django-admin startproject' using Django 3.0.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
import pymongo
from pymongo import MongoClient
from mongoengine import connect
from pymongo import mongo_client

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'e)974b&*2^u#^1ocw$#ajl$!9^rw(0w)98-bbhqulpe!negj9p'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['graffitiweb-c4.herokuapp.com', '127.0.0.1']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_xml',
    'rest_framework_mongoengine',
    'django_mongoengine',
    'django_mongoengine.mongo_auth',
    'django_mongoengine.mongo_admin',
    'drf_yasg',
    'graffitiApp',
    'ayuntamientoApp',
    'clienteApp',
    'corsheaders',
    'bootstrap4'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware'
]

CORS_ORIGIN_WHITELIST = (
  'http://localhost:8000',
  'http://127.0.0.1:8000',
  'graffitiweb-c4.herokuapp.com',
)

ROOT_URLCONF = 'graffitisWeb.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['/clientesApp/templates'],
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

WSGI_APPLICATION = 'graffitisWeb.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

# MongoDB Databases
MONGODB_DATABASES = {
    'default': {'name': 'iweb'}
}
# mongodb+srv://<username>:<password>@cluster0.pzn8b.mongodb.net/<dbname>?retryWrites=true&w=majority
# mongo_client.MongoClient.HOST = 'mongodb+srv://<username>:<password>@cluster0.pzn8b.mongodb.net/<dbname>?retryWrites=true&w=majority'
DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        'NAME': 'iweb',
        'HOST': 'mongodb+srv://Guest:guest@cluster0.pzn8b.mongodb.net/iweb?retryWrites=true&w=majority',
        'USER': 'Guest',
        'PASSWORD': 'guest',
    }
}

connect('iweb', host='mongodb+srv://Guest:guest@cluster0.pzn8b.mongodb.net/iweb?retryWrites=true&w=majority')

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

#AUTH_USER_MODEL = 'mongo_auth.MongoUser'

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
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

SESSION_ENGINE = 'mongo_sessions.session'
SESSION_SERIALIZER = 'django_mongoengine.sessions.BSONSerializer'

connection = MongoClient()
MONGO_CLIENT = connection.get_database(name='iweb')
MONGO_SESSIONS_COLLECTION = 'mongo_sessions' # default option

MONGOENGINE_USER_DOCUMENT = 'django_mongoengine'

# Django configuration
REST_FRAMEWORK = {
  'DEFAULT_PARSER_CLASSES': (
    'rest_framework.parsers.JSONParser',
    'rest_framework_xml.parsers.XMLParser',
    'rest_framework_csv.parsers.CSVParser'
  ),
    'DEFAULT_RENDERER_CLASSES': (
    'rest_framework.renderers.JSONRenderer',
    'rest_framework_xml.renderers.XMLRenderer',
    'rest_framework_csv.renderers.CSVRenderer'
  ),
}