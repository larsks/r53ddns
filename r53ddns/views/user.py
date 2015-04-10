import logging
from passlib.apps import custom_app_context as passlib

from fresco import Route, GET, POST, PUT, DELETE, PostArg
from fresco.exceptions import *

from r53ddns.utils import *
from r53ddns.model import *

LOG = logging.getLogger(__name__)


class UserManager (object):
    __routes__ = [
        Route('/debug', GET, 'debug'),
        Route('/<username:str>', GET, 'get_user'),
        Route('/<username:str>', DELETE, 'delete_user'),
        Route('/<username:str>', PUT, 'update_user',
              password=PostArg(default=None)),
        Route('/', GET, 'list_users'),
        Route('/', POST, 'create_user',
              username=PostArg(),
              password=PostArg(),
              is_admin=PostArg(int, default=0)),
    ]

    @json_response
    @db_session
    @is_admin
    def list_users(self):
        return [acc.to_dict() for acc in
                select(x for x in Account)]

    @json_response
    @db_session
    @is_admin_or_self
    def get_user(self, username):
        account = lookup_user(username)
        if not account:
            raise NotFound()
        return account.to_dict()

    @json_response
    @db_session
    @is_admin
    def create_user(self, username, password, is_admin=0):
        '''Create a new account.'''
        account = Account(name=username,
                      password=passlib.encrypt(password),
                      is_admin=is_admin)

        return {
            'status': 'created',
            'data': account.to_dict()}

    @json_response
    @db_session
    @is_admin_or_self
    def update_user(self, username, password=None):
        account = lookup_user(username)
        if not account:
            raise NotFound()

        if password is not None:
            account.password = passlib.encrypt(password)

        return {
            'status': 'updated',
            'data': account.to_dict()}

    @json_response
    @db_session
    @is_admin_or_self
    def delete_user(self, username):
        account = lookup_user(username)
        if not account:
            raise NotFound()

        save = account.to_dict()
        account.delete()

        return {'status': 'deleted',
                'data': save}
