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

import pony.orm
from fresco import Route, GET, POST, PUT, DELETE, Response, PostArg
from fresco.exceptions import *

from r53ddns.utils import *
from r53ddns.model import *
from r53ddns.exceptions import *

LOG = logging.getLogger(__name__)


class CredentialManager (object):
    __routes__ = [
        Route('/', GET, 'list_credentials'),
        Route('/', POST, 'create_credentials',
              accesskey=PostArg(),
              secretkey=PostArg(),
              label=PostArg(default=None)),
        Route('/<id:str>', GET, 'get_credentials'),
        Route('/<id:str>', PUT, 'update_credentials',
              accesskey=PostArg(default=None),
              secretkey=PostArg(default=None),
              label=PostArg(default=None)),
        Route('/<id:str>', DELETE, 'delete_credentials'),
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
    def create_credentials(self, username, accesskey, secretkey, label=None):
        account = lookup_user(username)
        if not account:
            raise NotFound()

        try:
            cred = Credentials(
                owner=account,
                accesskey=accesskey,
                secretkey=secretkey,
                name=label)
        except pony.orm.TransactionIntegrityError:
            raise Conflict()

        return (201, cred.to_dict())

    @json_response
    @db_session
    @is_admin_or_self
    def get_credentials(self, username, id):
        account = lookup_user(username)
        if not account:
            raise NotFound()

        cred = lookup_credentials_for(account, id)
        if not cred:
            raise NotFound()

        return cred.to_dict()

    @json_response
    @db_session
    @is_admin_or_self
    def update_credentials(self, username, id,
                           accesskey=None, secretkey=None, label=None):
        account = lookup_user(username)
        if not account:
            raise NotFound()

        cred = lookup_credentials_for(account, id)
        if not cred:
            raise NotFound()

        if accesskey is not None:
            cred.secrekey = accesskey
        if secretkey is not None:
            cred.secrekey = secretkey
        if label is not None:
            cred.name = label

        return cred.to_dict()

    @json_response
    @db_session
    @is_admin_or_self
    def delete_credentials(self, username, id):
        account = lookup_user(username)
        if not account:
            raise NotFound()

        cred = lookup_credentials_for(account, id)
        if not cred:
            raise NotFound()

        save = cred.to_dict()
        cred.delete()

        return save
