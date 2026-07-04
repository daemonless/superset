"""Daemonless Superset configuration -- bridges env vars to Superset config."""

import os

_home = os.environ.get("SUPERSET_HOME", "/config")

# SECRET_KEY: explicit env wins, else the key persisted by cont-init.
SECRET_KEY = os.environ.get("SUPERSET_SECRET_KEY", "")
if not SECRET_KEY:
    _key_file = os.path.join(_home, ".secret_key")
    if os.path.isfile(_key_file):
        with open(_key_file) as _f:
            SECRET_KEY = _f.read().strip()

# Metadata database: SQLite in /config by default, DATABASE_URL to override.
SQLALCHEMY_DATABASE_URI = os.environ.get(
    "DATABASE_URL", f"sqlite:///{os.path.join(_home, 'superset.db')}"
)

# Opt-in: allow SQLite database connections through the UI. Superset
# blocks them by default (file-access safety); for a self-contained
# appliance a local playground DB under /config is a reasonable trade.
if os.environ.get("SUPERSET_ALLOW_SQLITE", "").lower() in ("1", "true", "yes"):
    PREVENT_UNSAFE_DB_CONNECTIONS = False

# Redis-backed caching when REDIS_URL is set (optional).
_redis = os.environ.get("REDIS_URL", "")
if _redis:
    CACHE_CONFIG = {
        "CACHE_TYPE": "RedisCache",
        "CACHE_DEFAULT_TIMEOUT": 300,
        "CACHE_KEY_PREFIX": "superset_",
        "CACHE_REDIS_URL": _redis,
    }
