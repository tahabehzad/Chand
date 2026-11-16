"""Debug script to run downgrade and see actual error."""
import asyncio
import os
import sys

sys.path.insert(0, ".")

os.environ["DATABASE_URL"] = "postgresql+asyncpg://postgres@127.0.0.1:31918/pish_p0t04_migtest_d179a2f4cc"

from alembic import command
from alembic.config import Config
from app.core.config import get_settings

get_settings.cache_clear()
cfg = Config("alembic.ini")
cfg.set_main_option("script_location", "alembic")
cfg.attributes["connect_args"] = {"ssl": False, "server_settings": {"role": "pish_migration_owner"}}

# Monkey-patch to see actual error
import alembic.env as alembic_env
original_sanitized = alembic_env._sanitized_migration_failure

def debug_sanitized(exc):
    print(f"ACTUAL ERROR: {type(exc).__name__}: {exc}")
    import traceback
    traceback.print_exception(type(exc), exc, exc.__traceback__)
    return original_sanitized(exc)

alembic_env._sanitized_migration_failure = debug_sanitized

try:
    command.downgrade(cfg, "base")
    print("SUCCESS")
except Exception as e:
    print(f"FINAL ERROR: {type(e).__name__}: {e}")