# fastapi_watchlog_apm/__init__.py

from .instrument import instrument_app as instrument, instrument_app

__all__ = ["instrument_app"]

