"""
Error collector and error collector strategies.
"""

import enum
import threading
import typing as t
from .exceptions import FlexFailException, FailFastException


class ErrorCollectorStrategy(enum.StrEnum):
    """
    Available fail strategies:

    - ``skip`` - skip any exceptions raised.
    - ``fail_fast`` - raise the ``flexfail.exceptions.FailFastException`` when the first error occurs.
    - ``try_all`` - collects all the errors (no raise).
    """
    skip = enum.auto()
    fail_fast = enum.auto()
    try_all = enum.auto()


class ErrorCollector:
    """
    Flexible error collector, that supports multiple error collecting strategies.
    Please, refer to the ``flexfail.ErrorCollectorStrategy`` for more info about strategies.
    :param fn: callable object to catch the exceptions from.
    :param strategy: strategy to use.
    """
    def __init__(self, fn: t.Callable, strategy: ErrorCollectorStrategy):
        self._strategy = strategy
        self._fn = fn
        self._errors = []
        self._lock = threading.Lock()

    # Keep this name, not `__call__` so the doc-string is visible on hover.
    def call(self, *args, **kwargs):
        """
        Calls the provided on initialise callable and collects errors (if any).
        :param args: positional arguments for the callable.
        :param kwargs: keyword arguments for the callable.
        :return: object returned by the callable (if any).
        :raises flexfail.exceptions.FailFastException: if an error occurred in
        the callable and the strategy was ``fail_fast``.
        """
        try:
            return self._fn(*args, **kwargs)
        except FlexFailException as e:
            if self._strategy in (ErrorCollectorStrategy.fail_fast, ErrorCollectorStrategy.try_all):
                with self._lock:
                    self._errors.append(e)
            if self._strategy is ErrorCollectorStrategy.fail_fast:
                raise FailFastException('Failed fast!')

    @property
    def errors(self) -> t.List[FlexFailException]:
        """List of collected errors."""
        return self._errors