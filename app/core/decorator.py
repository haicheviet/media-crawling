from functools import wraps
from time import time


def decorator_logger_info(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        t0 = time()
        result = f(*args, **kwargs)
        kwargs["request"].app.logger.info(f"{f.__name__} function took {time() - t0}")
        return result

    return decorated
