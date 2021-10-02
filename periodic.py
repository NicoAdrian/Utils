import asyncio
import logging
import inspect
import random
from typing import Callable, Any, Union


class Periodic:
    """
    runs a callback every interval
    callback can be a sync or async function
    If 'jitter' is specified, each callback time will be randomly selected
    within a window of 'jitter * callback_time' milliseconds.
    Jitter can be used to reduce alignment of events with similar periods.
    A jitter of 0.1 means allowing a 10% variation in callback time
    """

    def __init__(self, callback: Callable[..., Any], interval: Union[int, float], jitter: float = 0.0) -> None:
        self.callback = callback
        self.interval = interval
        self.jitter = jitter
        self._running = False

    def start(self, run_now: bool = True) -> None:
        if not self.is_running():
            self._ioloop = asyncio.get_event_loop()
            self._running = True
            if run_now:
                res = self.callback()
                if inspect.isawaitable(res):
                    asyncio.ensure_future(res)
            self._schedule_next()

    def stop(self) -> None:
        if self.is_running():
            self._handle.cancel()
            self._running = False

    async def _run(self) -> None:
        try:
            res = self.callback()
            if inspect.isawaitable(res):
                await res
        except Exception as ex:
            logging.error(f"periodic callback '{self.callback.__name__}' error: {ex}")
        finally:
            self._schedule_next()

    def is_running(self) -> bool:
        return self._running

    def _schedule_next(self) -> None:
        self._handle = self._ioloop.call_later(
            self.interval * (1 + self.jitter * (random.random() - 0.5)), lambda: asyncio.ensure_future(self._run())
        )
