from fresco import Route, GET, POST, PUT, DELETE, Response
from fresco import PostArg, GetArg
from fresco import context
from fresco.exceptions import *

import route53

from ..utils import *
from ..model import *

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

        host = get(h for h in Host
                   if h.credentials.owner.id == account.id and
                   h.name == hostname)

        return host.to_dict()

    @json_response
    @db_session
    @is_admin_or_self
    def update_host(self, username, hostname, address=None):
        if address is None:
            address = context.request.environ['REMOTE_ADDR']

        account = lookup_user(username)
        if not account:
            raise NotFound()

        host = get(h for h in Host
                   if h.credentials.owner.id == account.id and
                   h.name == hostname)

        if not host:
            raise NotFound()

        amz = route53.connect(
            aws_access_key_id=host.credentials.accesskey,
            aws_secret_access_key=host.credentials.secretkey)

        try:
            zone = (z for z in amz.list_hosted_zones()
                    if z.name == host.zone + '.').next()
            rs = (r for r in zone.record_sets
                  if r.name == host.name + '.').next()
        except StopIteration:
            raise NotFound()

        rs.records = [address]
        rs.save()

        return {
            'status': 'updated',
            'data': {
                'address': address,
            }}

    @json_response
    @db_session
    @is_admin_or_self
    def create_host(self, username, hostname, credentials, zone=None):
        account = lookup_user(username)
        if not account:
            raise NotFound()

        cred = get(c for c in Credentials
                   if c.owner.id == account.id and
                   c.id == credentials)
        if not cred:
            raise NotFound()

        if zone is None:
            zone = '.'.join(hostname.split('.')[1:])

        host = Host(
            credentials=cred,
            zone=zone,
            name=hostname)

        return {
            'status': 'created',
            'data': host.to_dict()}