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

import base64
import logging

from passlib.apps import custom_app_context as passlib
from fresco.exceptions import *
from fresco import context

import r53ddns.model as model

__all__ = [
    'remote_addr',
    'lookup_user',
    'lookup_credentials_for',
    'lookup_host_for',
]

LOG = logging.getLogger(__name__)


def remote_addr():
    '''Return the client address, respecting the X-Forwarded-For header.'''

    env = context.request.environ
    address = env.get('HTTP_X_FORWARDED_FOR',
                      env['REMOTE_ADDR'])

    return address

def lookup_user(name_or_id):
    '''Look up a user by name or id.  If name_or_id is numeric it will be
    treated as an id, other we look for user accounts by name.'''
    if name_or_id.isdigit():
        return model.Account[int(name_or_id)]
    else:
        return model.get(obj for obj in model.Account
                         if obj.name == name_or_id)


def lookup_credentials_for(account, name_or_id):
    '''Find a credential set by name or id that is associated with the
    given account.  If name_or_id is numeric it will be treated as an
    id.'''
    if name_or_id.isdigit():
        return model.get(c for c in model.Credentials
                         if c.owner.id == account.id and
                         c.id == int(name_or_id))
    else:
        return model.get(c for c in model.Credentials
                         if c.owner.id == account.id and
                         c.name == name_or_id)


def lookup_host_for(account, name_or_id):
    '''Find a host record by name or id that is associated with the given
    account.  If name_or_id is numeric it will be treated as an id.'''
    if name_or_id.isdigit():
        return model.get(h for h in model.Host
                         if h.credentials.owner.id == account.id and
                         h.id == int(name_or_id))
    else:
        return model.get(h for h in model.Host
                         if h.credentials.owner.id == account.id and
                         h.name == name_or_id)


def verify_password(account, password_to_check):
    return passlib.verify(password_to_check, account.password)


@model.db_session
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
        if account is not None and verify_password(account, auth_pass):
            request.environ['requester'] = account
