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
from passlib.apps import custom_app_context as passlib

from fresco import Route, GET, POST, PUT, DELETE, PostArg
from fresco.exceptions import *

from r53ddns.utils import *
from r53ddns.model import *

LOG = logging.getLogger(__name__)


class UserManager (object):
    '''A class for managing user accounts.'''

    __routes__ = [
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
        '''Return a list of all user accounts. Requires admin access.'''
        return [account.to_dict(exclude='password') for account in
                select(account for account in Account)]

    @json_response
    @db_session
    @is_admin_or_self
    def get_user(self, username):
        '''Return information about a specific account.  You must either
        have admin access or be requesting information for the account with
        which you are currently authenticated.'''
        account = lookup_user(username)
        if not account:
            raise NotFound()
        return account.to_dict(exclude='password')

    @json_response
    @db_session
    @is_admin
    def create_user(self, username, password, is_admin=0):
        '''Create a new account.  Requires admin access.'''
        account = Account(name=username,
                          password=passlib.encrypt(password),
                          is_admin=is_admin)

        return account.to_dict(exclude='password')

    @json_response
    @db_session
    @is_admin_or_self
    def update_user(self, username, password=None):
        '''Update attributes on a user account. You must either have admin
        access or be modifying the account with which you authenticated.'''
        account = lookup_user(username)
        if not account:
            raise NotFound()

        if password is not None:
            account.password = passlib.encrypt(password)

        return account.to_dict(exclude='password')

    @json_response
    @db_session
    @is_admin_or_self
    def delete_user(self, username):
        '''Delete a user account. You must either have admin access or be
        deleting the account with which you authenticated.'''
        account = lookup_user(username)
        if not account:
            raise NotFound()

        save = account.to_dict(exclude='password')
        account.delete()

        return save
