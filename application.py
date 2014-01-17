#!/usr/bin/env python

import os
from r53ddns.webapp import app as application

if __name__ == '__main__':
    application.run(host=os.environ.get('OPENSHIFT_PYTHON_IP', '127.0.0.1'),
                    port=os.environ.get('OPENSHIFT_PYTHON_PORT', 8080))

