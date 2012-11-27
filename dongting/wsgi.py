import os
import sys

sys.path.append('/srv/www/dongting.fm/')
sys.path.append('/srv/www/dongting.fm/dongting')

os.environ['PYTHON_EGG_CACHE'] = '/srv/www/dongting.fm/.python-egg'
os.environ['DJANGO_SETTINGS_MODULE'] = 'dongting.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
