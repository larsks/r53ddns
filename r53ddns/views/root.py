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

from fresco import Route, GET, POST, PUT, DELETE, Response, PostArg
from fresco import context
from fresco.exceptions import *

from r53ddns.utils import *
from r53ddns.model import *


LOG = logging.getLogger(__name__)


class RootManager(object):
    __routes__ = [
        Route('/', GET, 'index'),
        Route('/debug', GET, 'debug'),
        Route('/ip', GET, 'ip'),
    ]

    def index(self):
        return Response('R53DDNS (http://github.com/larsks/r53ddns)\n')

    @json_response
    @db_session
    @is_admin
    def debug(self):
        return context.request.environ

    def ip(self):
        return Response(remote_addr() + '\n')
