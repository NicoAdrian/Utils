import logging
import asyncio
import functools
from typing import Callable, Any


def retry(n: int) -> Callable[..., Any]:
    def wrapper(f):
        err_msg = "Exception with function '{f}' with params {args} {kwargs}: {ex}; Retries left: {n}"
        # I hate code duplication but couldn't find a way to handle both sync and async functions
        if asyncio.iscoroutinefunction(f):

            @functools.wraps(f)
            async def inner(*args, **kwargs):
                nonlocal n
                while n >= 0:
                    try:
                        return await f(*args, **kwargs)
                    except Exception as ex:
                        if n == 0:
                            raise ex
                        else:
                            logging.warning(err_msg.format(f=f.__name__, args=args, kwargs=kwargs, ex=ex, n=n))
                            n -= 1

        else:

            @functools.wraps(f)
            def inner(*args, **kwargs):
                nonlocal n
                while n >= 0:
                    try:
                        return f(*args, **kwargs)
                    except Exception as ex:
                        if n == 0:
                            raise ex
                        else:
                            logging.warning(err_msg.format(f=f.__name__, args=args, kwargs=kwargs, ex=ex, n=n))
                            n -= 1

        return inner

    return wrapper
