from __future__ import annotations

import ipaddress
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class GeoResult:
    country: str = ''
    country_code: str = ''


def _is_private_ip(ip_str: str) -> bool:
    try:
        addr = ipaddress.ip_address(ip_str)
    except ValueError:
        return True
    return addr.is_private or addr.is_loopback or addr.is_reserved or addr.is_link_local or addr.is_unspecified


_lookup = None


def _get_lookup():
    global _lookup
    if _lookup is not None:
        return _lookup
    try:
        import geoip2.database  # type: ignore[import-untyped]
        import os
        from django.conf import settings
        db_path = getattr(settings, 'GEOIP_DATABASE_PATH', '') or os.getenv('GEOIP_DATABASE_PATH', '')
        if db_path:
            _lookup = geoip2.database.Reader(db_path)
            return _lookup
    except Exception:
        pass
    _lookup = False
    return None


def get_country_from_ip(ip_address: str) -> GeoResult:
    if not ip_address or _is_private_ip(ip_address):
        return GeoResult()
    reader = _get_lookup()
    if reader is None or reader is False:
        return GeoResult()
    try:
        resp = reader.country(ip_address)
        return GeoResult(
            country=resp.country.name or '',
            country_code=resp.country.iso_code or '',
        )
    except Exception:
        logger.debug('GeoIP lookup failed for %s', ip_address)
        return GeoResult()
