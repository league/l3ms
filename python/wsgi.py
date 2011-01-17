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

from django.conf import settings
settings.FORCE_SCRIPT_NAME = '/l3ms'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
