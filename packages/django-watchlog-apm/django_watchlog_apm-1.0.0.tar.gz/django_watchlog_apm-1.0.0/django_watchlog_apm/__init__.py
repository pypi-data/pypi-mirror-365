# django_watchlog_apm/__init__.py

from .instrument import instrument_django

# alias کوتاه‌تر
instrument = instrument_django

__all__ = [
    "instrument_django",
    "instrument",
]
