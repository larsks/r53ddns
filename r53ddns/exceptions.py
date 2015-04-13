from fresco import Response
from fresco.exceptions import *

class Conflict (ResponseException):

    response = Response(['Conflict'],
                        status=409)

