import os
import sys

VIRTUALENV = '/home/arungkci/virtualenv/arun_maira_site/3.11'
activate_this = VIRTUALENV + '/bin/activate_this.py'
with open(activate_this) as f:
    exec(f.read(), {'__file__': activate_this})

sys.path.insert(0, '/home/arungkci/arun_maira_site')
os.environ['DJANGO_SETTINGS_MODULE'] = 'arun_gateway.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
