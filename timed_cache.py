import collections
import time
import asyncio
import functools
from typing import Callable, Union, Any, Generator, Dict, Optional


class Cache(collections.abc.MutableMapping):
    def __init__(self, timeout: Union[int, float]):
        self.timeout = timeout
        self._mapping = {}  # type: Dict[Any, Any]
        self._sentinel = object()

    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        def get_key(args, kwargs):
            return args + (self._sentinel,) + tuple(sorted(kwargs.items()))

        if asyncio.iscoroutinefunction(func):

            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                key = get_key(args, kwargs)
                if key not in self:
                    self[key] = await func(*args, **kwargs)
                return self[key]

        else:

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                key = get_key(args, kwargs)
                if key not in self:
                    self[key] = func(*args, **kwargs)
                return self[key]

        return wrapper

    def __setitem__(self, k, v) -> None:
        self._mapping[k] = (v, time.time())

    def __getitem__(self, k) -> Optional[Any]:
        v, t = self._mapping[k]
        if time.time() - t > self.timeout:
            del self[k]
            raise KeyError(k)
        return v

    def __delitem__(self, k) -> None:
        del self._mapping[k]

    def __iter__(self) -> Generator[Any, Any, Any]:
        for k, (_, t) in self._mapping.items():
            if time.time() - t <= self.timeout:
                yield k

    def __len__(self) -> int:
        return sum(1 for _ in self)
