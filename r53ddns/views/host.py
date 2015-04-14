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
import datetime
import re

import route53
from pony.orm import TransactionIntegrityError
from fresco import Route, GET, POST, PUT, DELETE, Response
from fresco import PostArg, GetArg, context
from fresco.exceptions import *

import r53ddns.model as model
import r53ddns.utils as utils
from r53ddns.exceptions import *
from r53ddns.decorators import *

LOG = logging.getLogger(__name__)

re_ip = re.compile('\d+\.\d+\.\d+\.\d+')


class HostManager (object):
    __routes__ = [
        Route('/', GET, 'list_hosts'),
        Route('/', POST, 'create_host',
              kwargs={
                  'credentials': PostArg(),
                  'name': PostArg(),
                  'zone': PostArg(default=None),
              }),
        Route('/<hostname:str>', GET, 'get_host'),
        Route('/<hostname:str>', DELETE, 'delete_host'),
        Route('/<hostname:str>', PUT, 'update_host',
              kwargs={
                  'credentials': PostArg(default=None),
              }),
        Route('/<hostname:str>/address', GET, 'get_host_address'),
        Route('/<hostname:str>/address', POST, 'update_host_address',
              kwargs={
                'address': PostArg(default=None),
              }),
    ]

    @json_response
    @model.db_session
    @is_admin_or_self
    def list_hosts(self, username):
        account = utils.lookup_user(username)
        if not account:
            raise NotFound()

        hosts = model.select(host for host in model.Host
                             if host.credentials.owner.id == account.id)
        return [host.to_dict() for host in hosts]

    @json_response
    @model.db_session
    @is_admin_or_self
    def get_host(self, username, hostname):
        account = utils.lookup_user(username)
        if not account:
            raise NotFound()

        host = utils.lookup_host_for(account, hostname)
        if not host:
            raise NotFound()

        return host.to_dict()

    @json_response
    @model.db_session
    @is_admin_or_self
    def delete_host(self, username, hostname):
        account = utils.lookup_user(username)
        if not account:
            raise NotFound()

        host = utils.lookup_host_for(account, hostname)
        if not host:
            raise NotFound()

        save = host.to_dict()
        host.delete()
        return save

    @model.db_session
    @is_admin_or_self
    def get_host_address(self, username, hostname):
        account = utils.lookup_user(username)
        if not account:
            raise NotFound()

        host = utils.lookup_host_for(account, hostname)
        if not host:
            raise NotFound()

        return Response(host.last_address)

    @json_response
    @model.db_session
    @is_admin_or_self
    def update_host_address(self, username, hostname, address=None):
        if address is None or address == 'auto':
            address = utils.remote_addr()
        elif not re_ip.match(address):
            raise BadRequest()

        account = utils.lookup_user(username)
        if not account:
            raise NotFound()

        host = utils.lookup_host_for(account, hostname)
        if not host:
            raise NotFound()

        self.update_route53(host, address)

        host.last_update = datetime.datetime.utcnow()
        host.last_address = address

        return host.to_dict()

    def update_route53(self, host, address):
        if context.app.options.get('NO_ROUTE53_UPDATE'):
            LOG.info('skipping route53 update for %s',
                     host.name)
            return

        LOG.info('updating route53 for %s', host.name)

        amz = route53.connect(
            aws_access_key_id=host.credentials.accesskey,
            aws_secret_access_key=host.credentials.secretkey)

        try:
            zone = next(z for z in amz.list_hosted_zones()
                    if z.name == host.zone + '.')
            rs = next(r for r in zone.record_sets
                  if r.name == host.name + '.')
        except (StopIteration, TypeError):
            raise NotFound()

        rs.records = [address]
        rs.save()

    @json_response
    @model.db_session
    @is_admin_or_self
    def create_host(self, username, name, credentials, zone=None):
        account = utils.lookup_user(username)
        if not account:
            raise NotFound()

        cred = utils.lookup_credentials_for(account, credentials)
        if not cred:
            raise NotFound()

        if zone is None:
            zone = '.'.join(name.split('.')[1:])

        try:
            host = model.Host(
                credentials=cred,
                zone=zone,
                name=name)
            host.flush()
        except TransactionIntegrityError:
            raise Conflict()

        return (201, host.to_dict())

    @json_response
    @model.db_session
    @is_admin_or_self
    def update_host(self, username, hostname,
                    credentials=None):
        account = utils.lookup_user(username)
        if not account:
            raise NotFound()

        host = utils.lookup_host_for(account, hostname)
        if not host:
            raise NotFound()

        if credentials is not None:
            cred = utils.lookup_credentials_for(account, credentials)
            if not cred:
                raise NotFound()
            host.credentials = cred

        return host.to_dict()
