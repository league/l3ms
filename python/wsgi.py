import os                       # -*- python -*-
import sys
from os.path import realpath, dirname

# Set path to find l3ms/ python dir.
sys.path.append(dirname(realpath(__file__)))

# Set environment for Django.
os.environ['DJANGO_SETTINGS_MODULE'] = 'l3ms.settings'

# Set prefix to empty string; this script mounted at /l3ms/ already.
import l3ms.settings
l3ms.settings.URL_PREFIX = ''

# Recommendations for production use:
# 1. Turn off DEBUG mode
#l3ms.settings.DEBUG = False
# 2. Set SECRET_KEY to something not from source repo
# 3. Set DATABASE_ settings to use ident auth from www-data


import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
