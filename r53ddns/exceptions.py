from fresco import Response
from fresco.exceptions import *

class Conflict (ResponseException):

    '''The request could not be completed due to a conflict with the
    current state of the resource. This code is only allowed in situations
    where it is expected that the user might be able to resolve the
    conflict and resubmit the request.'''

    response = Response(['Conflict'],
                        status=409)
