from __future__ import annotations

import gzip
import os
import shutil
import tarfile
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

MAXMIND_DOWNLOAD_URL = (
    'https://download.maxmind.com/geoip/databases/GeoLite2-Country/download?suffix=tar.gz'
)
DEFAULT_GEOIP_DATABASE_PATH = '/opt/render/project/geoip/GeoLite2-Country.mmdb'
_MMDB_NAME = 'GeoLite2-Country.mmdb'


class GeoIPDownloadError(Exception):
    pass


def resolve_geoip_database_path(explicit_path: str = '') -> str:
    path = (explicit_path or os.getenv('GEOIP_DATABASE_PATH', '')).strip()
    return path or DEFAULT_GEOIP_DATABASE_PATH


def download_geolite2_country(
    dest_path: str = '',
    account_id: str = '',
    license_key: str = '',
) -> str:
    account_id = (account_id or os.getenv('MAXMIND_ACCOUNT_ID', '')).strip()
    license_key = (license_key or os.getenv('MAXMIND_LICENSE_KEY', '')).strip()
    dest = Path(resolve_geoip_database_path(dest_path))

    if not account_id or not license_key:
        raise GeoIPDownloadError(
            'GeoLite2-Country download skipped: MAXMIND_ACCOUNT_ID and '
            'MAXMIND_LICENSE_KEY must both be set.'
        )

    dest.parent.mkdir(parents=True, exist_ok=True)
    password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
    password_mgr.add_password(None, MAXMIND_DOWNLOAD_URL, account_id, license_key)
    opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler(password_mgr))

    try:
        with opener.open(MAXMIND_DOWNLOAD_URL, timeout=60) as response:
            archive_bytes = response.read()
    except urllib.error.HTTPError as exc:
        raise GeoIPDownloadError(
            f'GeoLite2-Country download failed: HTTP {exc.code} from MaxMind.'
        ) from None
    except urllib.error.URLError:
        raise GeoIPDownloadError(
            'GeoLite2-Country download failed: could not reach MaxMind.'
        ) from None

    mmdb_bytes = _extract_mmdb(archive_bytes)
    _atomic_write(dest, mmdb_bytes)
    return str(dest)


def _extract_mmdb(archive_bytes: bytes) -> bytes:
    with tempfile.TemporaryDirectory() as tmp:
        archive_path = Path(tmp) / 'geolite2-country.tar.gz'
        archive_path.write_bytes(archive_bytes)
        try:
            with tarfile.open(archive_path, 'r:gz') as tar:
                member = _find_mmdb_member(tar)
                extracted = tar.extractfile(member)
                if extracted is None:
                    raise GeoIPDownloadError(
                        'GeoLite2-Country download failed: archive did not contain a readable .mmdb.'
                    )
                return extracted.read()
        except tarfile.TarError:
            pass
        try:
            return gzip.decompress(archive_bytes)
        except OSError:
            raise GeoIPDownloadError(
                'GeoLite2-Country download failed: response was not a valid GeoLite2 archive.'
            ) from None


def _find_mmdb_member(tar: tarfile.TarFile) -> tarfile.TarInfo:
    for member in tar.getmembers():
        if member.isfile() and member.name.endswith(_MMDB_NAME):
            return member
    raise GeoIPDownloadError(
        'GeoLite2-Country download failed: archive did not contain GeoLite2-Country.mmdb.'
    )


def _atomic_write(dest: Path, data: bytes) -> None:
    fd, tmp_name = tempfile.mkstemp(prefix='.geolite2-', suffix='.mmdb', dir=dest.parent)
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, 'wb') as handle:
            handle.write(data)
        shutil.move(str(tmp_path), str(dest))
    except Exception:
        tmp_path.unlink(missing_ok=True)
        raise
