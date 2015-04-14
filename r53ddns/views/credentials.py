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

import logging

from pony.orm import TransactionIntegrityError, ConstraintError
from fresco import Route, GET, POST, PUT, DELETE, Response, PostArg
from fresco.exceptions import *

import r53ddns.model as model
import r53ddns.utils as utils
from r53ddns.exceptions import *
from r53ddns.decorators import *

LOG = logging.getLogger(__name__)


class CredentialManager (object):
    __routes__ = [
        Route('/', GET, 'list_credentials'),
        Route('/', POST, 'create_credentials',
              kwargs={
                  'accesskey': PostArg(),
                  'secretkey': PostArg(),
                  'name': PostArg(default=None),
              }),
        Route('/<id:str>', GET, 'get_credentials'),
        Route('/<id:str>', PUT, 'update_credentials',
              kwargs={
                  'accesskey': PostArg(default=None),
                  'secretkey': PostArg(default=None),
                  'name': PostArg(default=None),
              }),
        Route('/<id:str>', DELETE, 'delete_credentials'),
    ]

    @json_response
    @model.db_session
    @is_admin_or_self
    def list_credentials(self, username):
        account = utils.lookup_user(username)
        if not account:
            raise NotFound()

        creds = model.select(cred for cred in model.Credentials
                       if cred.owner.id == account.id)
        return [cred.to_dict() for cred in creds]

    @json_response
    @model.db_session
    @is_admin_or_self
    def create_credentials(self, username, accesskey, secretkey, name=None):
        account = utils.lookup_user(username)
        if not account:
            raise NotFound()

        try:
            cred = model.Credentials(
                owner=account,
                accesskey=accesskey,
                secretkey=secretkey,
                name=name)
            cred.flush()
        except TransactionIntegrityError:
            raise Conflict()

        return (201, cred.to_dict())

    @json_response
    @model.db_session
    @is_admin_or_self
    def get_credentials(self, username, id):
        account = utils.lookup_user(username)
        if not account:
            raise NotFound()

        cred = utils.lookup_credentials_for(account, id)
        if not cred:
            raise NotFound()

        return cred.to_dict()

    @json_response
    @model.db_session
    @is_admin_or_self
    def update_credentials(self, username, id,
                           accesskey=None, secretkey=None, name=None):
        account = utils.lookup_user(username)
        if not account:
            raise NotFound()

        cred = utils.lookup_credentials_for(account, id)
        if not cred:
            raise NotFound()

        if accesskey is not None:
            cred.accesskey = accesskey
        if secretkey is not None:
            cred.secretkey = secretkey
        if name is not None:
            cred.name = name

        return cred.to_dict()

    @json_response
    @model.db_session
    @is_admin_or_self
    def delete_credentials(self, username, id):
        account = utils.lookup_user(username)
        if not account:
            raise NotFound()

        cred = utils.lookup_credentials_for(account, id)
        if not cred:
            raise NotFound()

        save = cred.to_dict()

        try:
            cred.delete()
        except ConstraintError:
            raise Conflict()

        return save
