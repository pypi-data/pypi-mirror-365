from __future__ import annotations

import functools
import logging
from collections.abc import Callable

from typing_extensions import TYPE_CHECKING, Any, Optional, ParamSpec, TypeVar

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .database import Database


class DatabaseEntity:
    """
    Base class for all Database entities.
    """

    def __init__(self, database: Optional[Database]):
        """
        Constructs a database entity for the given database.

        Args:
            database: Reference to the active IDA database.
        """
        self.m_database = database


F = TypeVar('F', bound=Callable[..., Any])
C = TypeVar('C', bound=type)
P = ParamSpec('P')
R = TypeVar('R')


class DatabaseNotLoadedError(RuntimeError):
    """Raised when an operation is attempted on a closed database."""

    pass


def decorate_all_methods(decorator: Callable[[F], F]) -> Callable[[C], C]:
    """
    Class decorator factory that applies `decorator` to all methods
    of the class (excluding dunder methods and static methods).
    """

    def decorate(cls: C) -> C:
        for name, attr in cls.__dict__.items():
            if name.startswith('__'):
                continue
            # Skip static methods and class methods
            if isinstance(attr, (staticmethod, classmethod)):
                continue
            if callable(attr):
                setattr(cls, name, decorator(attr))
        return cls

    return decorate


def check_db_open(fn: Callable[P, R]) -> Callable[P, R]:
    """
    Decorator that checks that a database is open.
    """

    @functools.wraps(fn)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        # Check inside database class
        if args:
            self = args[0]

            # Check class name as string (avoid circular dependency)
            if self.__class__.__name__ == 'Database':
                if hasattr(self, 'is_open') and not self.is_open():
                    raise DatabaseNotLoadedError(
                        f'{fn.__qualname__}: Database is not loaded. Please open a database first.'
                    )

            # Check DatabaseEntity instances
            if isinstance(self, DatabaseEntity):
                if not self.m_database or not self.m_database.is_open():
                    raise DatabaseNotLoadedError(
                        f'{fn.__qualname__}: Database is not loaded. Please open a database first.'
                    )

        return fn(*args, **kwargs)

    return wrapper
