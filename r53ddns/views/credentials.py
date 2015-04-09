from fresco import Route, GET, POST, PUT, DELETE, Response, PostArg
from fresco import context
from fresco.exceptions import *

from ..utils import *
from ..model import *


class CredentialManager (object):
    __routes__ = [
        Route('/', GET, 'list_credentials'),
        Route('/', POST, 'create_credentials',
              accesskey=PostArg(),
              secretkey=PostArg(),
              credname=PostArg()),
        Route('/<id:int>', GET, 'get_credentials'),
        Route('/<id:int>', DELETE, 'delete_credentials'),
    ]

    @json_response
    @db_session
    @is_admin_or_self
    def list_credentials(self, username):
        account = lookup_user(username)
        if not account:
            raise NotFound()

        creds = select(cred for cred in Credentials
                       if cred.owner.id == account.id)
        return [cred.to_dict() for cred in creds]

    @json_response
    @db_session
    @is_admin_or_self
    def create_credentials(self, username, accesskey, secretkey, credname=None):
        account = lookup_user(username)
        if not account:
            raise NotFound()

        cred = Credentials(
            owner=account,
            accesskey=accesskey,
            secretkey=secretkey,
            name=credname)

        return {'status': 'created',
                'data': cred.to_dict()}


    @json_response
    @db_session
    @is_admin_or_self
    def get_credentials(self, username, id):
        account = lookup_user(username)
        if not account:
            raise NotFound()

        cred = get(c for c in Credentials
                   if c.owner.id == account.id and
                   c.id == id)
        if not cred:
            raise NotFound()

        return cred.to_dict()

    @json_response
    @db_session
    @is_admin_or_self
    def delete_credentials(self, username, id):
        account = lookup_user(username)
        if not account:
            raise NotFound()

        cred = get(c for c in Credentials
                   if c.owner.id == account.id and
                   c.id == id)
        if not cred:
            raise NotFound()

        save = cred.to_dict()
        cred.delete()

        return {
            'status': 'deleted',
            'data': save,
        }
