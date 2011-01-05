# Django settings for l3ms project.

from os.path import realpath, dirname, join

PROJECT_ROOT = dirname(dirname(dirname(realpath(__file__))))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

URL_PREFIX = 'l3ms/'           # Django script mounted at actual root
LOGIN_URL = '/l3ms/'

HTTP_AUTH_REALM = 'Secure area'
HTTP_AUTH_DEBUG = False

SITE_NAME = 'liucs.net'
FROM_EMAIL = 'noreply@liucs.net'

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'postgresql_psycopg2'
DATABASE_NAME = 'djlms'
DATABASE_USER = 'djlms'
DATABASE_PASSWORD = 'wIfPF9ICqksCHNi9'
DATABASE_HOST = 'localhost'
DATABASE_PORT = ''

if DEBUG:
    EMAIL_PORT = 1025

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/django-media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'rlser#(u)qctvs48j59-1zc%ydjcuxu)#@m=m2966!+j_6_&^d'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

AUTH_PROFILE_MODULE = 'accounts.UserProfile'

ROOT_URLCONF = 'l3ms.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    join(PROJECT_ROOT, 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'l3ms.misc',
    'l3ms.accounts',
    'l3ms.courses',
    'l3ms.http_auth',
    'l3ms.email_validation',
)
