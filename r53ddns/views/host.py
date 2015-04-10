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

from fresco import Route, GET, POST, PUT, DELETE, Response
from fresco import PostArg, GetArg, context
from fresco.exceptions import *

import route53

from r53ddns.utils import *
from r53ddns.model import *

LOG = logging.getLogger(__name__)


class HostManager (object):
    __routes__ = [
        Route('/', GET, 'list_hosts'),
        Route('/', POST, 'create_host',
              credentials=PostArg(),
              hostname=PostArg(),
              zone=PostArg(default=None)),
        Route('/<hostname:str>', GET, 'get_host'),
        Route('/<hostname:str>/update', GET, 'update_host',
              address=GetArg(default=None)),
    ]

    @json_response
    @db_session
    @is_admin_or_self
    def list_hosts(self, username):
        account = lookup_user(username)
        if not account:
            raise NotFound()

        hosts = select(host for host in Host
                       if host.credentials.owner.id == account.id)
        return [host.to_dict() for host in hosts]

    @json_response
    @db_session
    @is_admin_or_self
    def get_host(self, username, hostname):
        account = lookup_user(username)
        if not account:
            raise NotFound()

        host = lookup_host_for(account, hostname)
        if not host:
            raise NotFound()

        return host.to_dict()

    @json_response
    @db_session
    @is_admin_or_self
    def update_host(self, username, hostname, address=None):
        if address is None:
            address = remote_addr()

        account = lookup_user(username)
        if not account:
            raise NotFound()

        host = lookup_host_for(account, hostname)
        if not host:
            raise NotFound()

        self.update_route53(host)

        host.last_update = datetime.datetime.utcnow()
        host.last_address = address

        return host.to_dict()

    def update_route53(self, host):
        if context.app.options.get('NO_ROUTE53_UPDATE'):
            LOG.info('skipping route53 update for %s',
                     host.name)
            return

        LOG.info('updating route53 for %s', host.name)

        amz = route53.connect(
            aws_access_key_id=host.credentials.accesskey,
            aws_secret_access_key=host.credentials.secretkey)

        try:
            zone = (z for z in amz.list_hosted_zones()
                    if z.name == host.zone + '.').next()
            rs = (r for r in zone.record_sets
                  if r.name == host.name + '.').next()
        except (StopIteration, TypeError):
            raise NotFound()

        rs.records = [address]
        rs.save()

    @json_response
    @db_session
    @is_admin_or_self
    def create_host(self, username, hostname, credentials, zone=None):
        account = lookup_user(username)
        if not account:
            raise NotFound()

        cred = lookup_credentials_for(account, credentials)
        if not cred:
            raise NotFound()

        if zone is None:
            zone = '.'.join(hostname.split('.')[1:])

        host = Host(
            credentials=cred,
            zone=zone,
            name=hostname)

        return host.to_dict()
