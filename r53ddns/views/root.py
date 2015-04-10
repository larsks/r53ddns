from fresco import Route, GET, POST, PUT, DELETE, Response, PostArg
from fresco import context
from fresco.exceptions import *

from ..utils import *
from ..model import *

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
