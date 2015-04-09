from fresco import Response, context
from fresco.exceptions import *
import json
import datetime
from decorator import decorator

def json_dumps_helper(data):
    if isinstance(data, datetime.datetime):
        return str(data)

@decorator
def json_response(func, *args, **kwargs):
    res = func(*args, **kwargs)
    return Response(json.dumps(res, indent=2, default=json_dumps_helper),
                    content_type='application/json')


@decorator
def require_admin(func, *args, **kwargs):
    print dir(context.request)
    return func(*args, **kwargs)

