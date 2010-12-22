import os                       # -*- python -*-
import sys
from os.path import realpath, dirname

sys.path.append(dirname(dirname(realpath(__file__))))

import djlms.settings

# Recommendations for production use:
# 1. Turn off DEBUG mode
#djlms.settings.DEBUG = False
# 2. Set SECRET_KEY to something not from source repo
# 3. Set DATABASE_ settings to use ident auth from www-data

os.environ['DJANGO_SETTINGS_MODULE'] = 'djlms.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
