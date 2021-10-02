import functools
import asyncio


def run_in_executor(f):
    """
    Enable us to run any function in a separate thread or process, depending of the current executor (default is thread)
    """

    @functools.wraps(f)
    async def wrapper(*args, **kwargs):
        return await asyncio.get_event_loop().run_in_executor(None, functools.partial(f, *args, **kwargs))

    return wrapper
