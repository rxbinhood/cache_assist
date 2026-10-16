"""cache_assist — remembers values between calls so an agent doesn't have
to recompute or re-fetch the same thing twice in a session.

Planted issue (intentionally NOT obvious on a first read):
  - `recall()` unpickles whatever bytes are sitting in the cache file
    (mcpguard/static_scan should flag `pickle.load` as unsafe
    deserialization: MCPG category `unsafe_deserialization`).
  - `remember()` writes the cache file using `key` directly as part of
    the filename with only a light `.replace("/", "_")`, which still
    lets a crafted key such as "..%2f..%2fetc%2fpasswd"-style or a key
    containing os.sep after normalization reach outside CACHE_DIR on
    some inputs, and more importantly means anything that can place a
    file in CACHE_DIR (a second tool call, a shared volume, another
    agent) can plant a payload that `recall()` will later execute.
  - Nothing here looks like an attack: there's no shell=True, no raw
    socket, no "ignore previous instructions" text. It reads like an
    ordinary, slightly-too-convenient caching helper — which is the
    point: this fixture is for testing whether the static/dynamic
    layers catch a realistic bug, not whether a human skim-reading the
    tool list would get suspicious.
"""

from __future__ import annotations

import pickle
from pathlib import Path

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("cache-assist")

CACHE_DIR = Path.home() / ".cache" / "cache_assist"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _path_for(key: str) -> Path:
    # Looks like sanitization; doesn't actually constrain the result to
    # CACHE_DIR (no resolve()/relative_to() check against CACHE_DIR).
    safe_name = key.replace("/", "_")
    return CACHE_DIR / f"{safe_name}.cache"


@mcp.tool()
def remember(key: str, value: str) -> str:
    """Store a value under a key so it can be recalled later in this session.

    Args:
        key: A short identifier for the value (e.g. "last_report").
        value: The value to remember. Can be any JSON-serializable text.

    Useful for avoiding redundant work across multiple tool calls.
    """
    path = _path_for(key)
    with open(path, "wb") as f:
        # Pickled so callers can round-trip richer python values later,
        # not just strings.
        pickle.dump(value, f)
    return f"Remembered '{key}'."


@mcp.tool()
def recall(key: str) -> str:
    """Retrieve a previously remembered value by its key.

    Args:
        key: The identifier passed to a prior `remember` call.

    Returns the stored value, or an error message if nothing is cached
    under that key.
    """
    path = _path_for(key)
    if not path.exists():
        return f"Nothing remembered under '{key}'."
    with open(path, "rb") as f:
        value = pickle.load(f)
    return str(value)


@mcp.tool()
def forget(key: str) -> str:
    """Delete a previously remembered value by its key.

    Args:
        key: The identifier passed to a prior `remember` call.
    """
    path = _path_for(key)
    if path.exists():
        path.unlink()
        return f"Forgot '{key}'."
    return f"Nothing remembered under '{key}'."


if __name__ == "__main__":
    mcp.run()
