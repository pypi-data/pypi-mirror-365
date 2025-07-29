"""
Utilities for performing slow processing tasks in a background thread.
"""

from typing import Generic, TypeVar, Callable

from threading import Thread


T = TypeVar("T")


class CachedBackgroundCall(Generic[T]):
    """
    Eagerly execute a function call in a background thread and cache the result
    to be returned on demand.

    Exmaple::

        >>> c = CachedCall(some_slow_function)
        >>> c.ready
        False
        >>> c()  # Will block since the function is still running
        "I'm the slow function's output. Ta-da!"
        >>> c.ready
        True
        >>> c()  # Function already finished, returning cached value is instant!
        "I'm the slow function's output. Ta-da!"
    """

    _thread: Thread
    _result: T
    _exc: Exception | None

    def __init__(self, fn: Callable[[], T]) -> None:
        self._thread = Thread(target=self._run, args=(fn,), daemon=True)
        self._thread.start()

    def _run(self, fn: Callable[[], T]) -> None:
        try:
            self._result = fn()
            self._exc = None
        except Exception as exc:
            self._exc = exc

    @property
    def ready(self) -> bool:
        """True if calling will return immediately, False otherwise."""
        return not self._thread.is_alive()

    def __call__(self) -> T:
        """
        Read the value returned by the function. Will block until the function
        finishes executing if it hasn't already.
        """
        self._thread.join()

        if self._exc is not None:
            raise self._exc
        else:
            return self._result
