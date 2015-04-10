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
    res = func(*args, **kwargs)
    return Response(json.dumps(res, indent=2, default=json_dumps_helper),
                    content_type='application/json')


def _is_authenticated():
    env = context.request.environ
    return env.get('requester') is not None


@decorator
def is_authenticated(func, *args, **kwargs):
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
    else:
        return requester.is_admin


@decorator
def is_admin(func, *args, **kwargs):
    if not _is_admin():
        raise Forbidden()

    return func(*args, **kwargs)


def _is_admin_or_self(username):
    env = context.request.environ

    return _is_admin() or (_is_authenticated() and
                           env['requester'].name == username)


@decorator
def is_admin_or_self(func, *args, **kwargs):
    if not _is_admin_or_self(args[1]):
        raise Forbidden()

    return func(*args, **kwargs)


def remote_addr():
    env = context.request.environ

    address = env.get('HTTP_X_FORWARDED_FOR',
                      env['REMOTE_ADDR'])

    return address
