from fresco import Route, GET, POST, Response

class RootManager(object):
    __routes__ = [
        Route('/', GET, 'index'),
    ]

    def index(self):
        return Response('R53DDNS (http://github.com/larsks/r53ddns)\n')

