# r53ddns -- dynamic dns server for Route53
# Copyright (C) 2015 Lars Kellogg-Stedman
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
from fresco import FrescoApp
import base64
import logging
from passlib.apps import custom_app_context as passlib

import r53ddns.views as views
from r53ddns.model import *

LOG = logging.getLogger(__name__)

config = {
    'DATABASE': 'sample.db',
    'ADMIN_NAME': 'admin',
}

app = FrescoApp()
app.options.update(config)
app.options.update_from_file(os.path.join(
    os.environ.get('OPENSHIFT_DATA_DIR', '.'),
    'settings.py'))

setup_database(app.options.DATABASE)

app.include('/user/<username:str>/credentials', views.CredentialManager())
app.include('/user/<username:str>/host', views.HostManager())
app.include('/user', views.UserManager())
app.include('/', views.RootManager())


@app.process_request
@db_session
def extract_auth_info(request):
    '''This runs at the beginning of each request and provisions
    a `requester` key in request.environ if the client has provided valid
    credentials.'''

    auth = request.get_header('authorization')

    if not auth:
        return

    auth_type, auth_data = auth.split(None, 1)
    request.environ['auth_data'] = auth_data
    request.environ['auth_type'] = auth_type

    if auth_type == 'Basic':
        auth_data = base64.decodestring(auth_data)
        auth_name, auth_pass = auth_data.split(':', 1)
        request.environ['auth_name'] = auth_name
        request.environ['auth_pass'] = auth_pass

        LOG.info('authenticating request to %s by %s',
                 request.url, auth_name)

        account = lookup_user(auth_name)
        if account and passlib.verify(auth_pass, account.password):
            request.environ['requester'] = account
