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

from decorator import decorator
from fresco.exceptions import *
from fresco import Response, context
import json
import datetime

from r53ddns.model import *

__all__ = [
    'json_response',
    'is_admin',
    'is_authenticated',
    'is_admin_or_self',
    'remote_addr',
]


def json_dumps_helper(data):
    if isinstance(data, datetime.datetime):
        return str(data)


@decorator
def json_response(func, *args, **kwargs):
    '''Serializes the response from the wrapped function using JSON.  If
    the function returns a tuple, assume that the first item is a desired
    HTTP status code and the second item contains the response data.'''

    res = func(*args, **kwargs)
    if isinstance(res, tuple):
        status, res = res
    else:
        status = 200

    return Response(json.dumps(res, indent=2, default=json_dumps_helper),
                    status=status,
                    content_type='application/json')


def _is_authenticated():
    env = context.request.environ
    return env.get('requester') is not None


@decorator
def is_authenticated(func, *args, **kwargs):
    '''Return an HTTP 403 (Forbidden) response if the user is not
    authenticated.'''

    if not _is_authenticated():
        raise Forbidden()

    return func(*args, **kwargs)


def _is_admin():
    env = context.request.environ

    requester = env.get('requester')
    auth_name = env.get('auth_name')
    auth_pass = env.get('auth_pass')

    admin_name = context.app.options.get('ADMIN_NAME')
    admin_pass = context.app.options.get('ADMIN_PASSWORD')

    if requester is None and admin_name and admin_pass:
        if auth_name == admin_name and auth_pass == admin_pass:
            return True
    elif requester is not None:
        return requester.is_admin
    else:
        return False


@decorator
def is_admin(func, *args, **kwargs):
    '''Return an HTTP 403 (Forbidden) response if the user does not have
    administrative privileges.'''

    if not _is_admin():
        raise Forbidden()

    return func(*args, **kwargs)


def _is_admin_or_self(username):
    env = context.request.environ

    return _is_admin() or (_is_authenticated() and
                           env['requester'].name == username)


@decorator
def is_admin_or_self(func, *args, **kwargs):
    '''Return an HTTP 403 (Forbidden) response if the user is not an
    administrator AND is trying to access a resource not owned by the
    requesting user.'''

    if not _is_admin_or_self(args[1]):
        raise Forbidden()

    return func(*args, **kwargs)


def remote_addr():
    '''Return the client address, respecting the X-Forwarded-For header.'''

    env = context.request.environ
    address = env.get('HTTP_X_FORWARDED_FOR',
                      env['REMOTE_ADDR'])

    return address
