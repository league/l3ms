import os                       # -*- python -*-
import sys
from os.path import realpath, dirname

sys.path.append(dirname(dirname(realpath(__file__))))

import djlms.settings
#djlms.settings.DEBUG = False
os.environ['DJANGO_SETTINGS_MODULE'] = 'djlms.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
