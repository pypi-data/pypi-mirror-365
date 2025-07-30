# path: timing/api.py (replace the whole file)
import functools
from contextlib import contextmanager
from typing import Any, Callable, Dict, Optional  # <<< FIX: Import Optional
from uuid import UUID

from .engine import get_engine


@contextmanager
def time_block(marker_name: str, tags: Dict[str, Any] = None, **kwargs: Any):
    """
    A context manager to time a block of code.
    :param marker_name: The name for this timing event.
    :param tags: A dictionary of key-value pairs for grouping and analysis.
    :param kwargs: For backward compatibility, context can be passed as kwargs.
    """
    engine = get_engine()
    if not engine.is_enabled():
        yield
        return

    final_tags = {**(tags or {}), **kwargs}

    event_id = engine.start_event(marker_name, final_tags)
    try:
        yield
    finally:
        if event_id:
            engine.stop_event(event_id)


def time_function(
    _func: Callable = None, *, tags: Dict[str, Any] = None, **kwargs: Any
):
    """
    A decorator to time an entire function. Can be used with or without arguments.

    Usage:
        @time_function
        def my_func(): ...

        @time_function(tags={'component': 'auth'})
        def another_func(): ...
    """
    final_tags = {**(tags or {}), **kwargs}

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            engine = get_engine()
            if not engine.is_enabled():
                return func(*args, **kwargs)

            marker_name = func.__name__
            with time_block(marker_name, tags=final_tags):
                return func(*args, **kwargs)

        return wrapper

    if _func is None:
        # Called as @time_function(tags=...)
        return decorator
    else:
        # Called as @time_function
        return decorator(_func)


def time_start(
    marker_name: str, tags: Dict[str, Any] = None, **kwargs: Any
) -> Optional[UUID]:  # <<< FIX: Changed "UUID | None" to "Optional[UUID]"
    """
    Manually starts a timer and returns a unique event ID.
    :param marker_name: The name for this timing event.
    :param tags: A dictionary of key-value pairs for grouping and analysis.
    :param kwargs: For backward compatibility, context can be passed as kwargs.
    """
    engine = get_engine()
    if not engine.is_enabled():
        return None

    final_tags = {**(tags or {}), **kwargs}
    return engine.start_event(marker_name, final_tags)


def time_stop(event_id: UUID):
    """
    Manually stops a timer using the event ID from time_start.
    The tags are associated at time_start and do not need to be passed here.
    """
    engine = get_engine()
    if not engine.is_enabled() or not event_id:
        return
    engine.stop_event(event_id)

