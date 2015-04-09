from fresco import Route, GET, POST, PUT, DELETE, Response, PostArg
from fresco import context
from fresco.exceptions import *

from ..utils import json_response, require_admin
from ..model import *

class UserManager (object):
    __routes__ = [
        Route('/debug', GET, 'debug'),
        Route('/<username:str>', GET, 'get_user'),
        Route('/<username:str>', DELETE, 'delete_user'),
        Route('/', GET, 'list_users'),
        Route('/', POST, 'create_user',
              username=PostArg(),
              password=PostArg()),
    ]

    @json_response
    @db_session
    def list_users(self):
        return [acc.to_dict() for acc in
                select(x for x in Account)]

    @json_response
    @db_session
    def get_user(self, username):
        account = lookup_user(username)
        if not account:
            raise NotFound()
        return account.to_dict()

    @json_response
    @db_session
    def create_user(self, username, password):
        '''Create a new account.'''
        acc = Account(name=username,
                      password=password)

        return {
            'status': 'created',
            'data': acc.to_dict()}

    @json_response
    @db_session
    def delete_user(self, username):
        account = lookup_user(username)
        if not account:
            raise NotFound()

        save = account.to_dict()
        account.delete()

        return {'status': 'deleted',
                'data': save}

    @json_response
    @db_session
    def debug(self):
        return context.request.environ
