#!/usr/bin/python
import os
import logging

if 'OPENSHIFT_PYTHON_DIR' in os.environ:
    virtenv = os.environ['OPENSHIFT_PYTHON_DIR'] + '/virtenv/'
    virtualenv = os.path.join(virtenv, 'bin/activate_this.py')
    try:
        execfile(virtualenv, dict(__file__=virtualenv))
    except IOError:
        pass

#
# IMPORTANT: Put any additional includes below this line.  If placed above this
# line, it's possible required libraries won't be in your searchable path
#

logging.basicConfig(level='INFO')

import r53ddns.app

datadir = os.environ.get('OPENSHIFT_DATA_DIR', '.')
application = r53ddns.app.R53DDNS(
    config_file=os.path.join(datadir, 'settings.py'))
