"""Version fetching for Plone, Volto, Python, and Node.js.

Data sources:
- Plone versions: https://dist.plone.org/release/
- Python compatibility: Products.CMFPlone PyPI classifiers
- Volto versions: npm registry @plone/volto
- Node compatibility: @plone/volto engines.node field
"""
from __future__ import annotations

import re
from functools import lru_cache
from typing import Any

import httpx


DIST_PLONE_URL = "https://dist.plone.org/release/"
PYPI_URL = "https://pypi.org/pypi"
NPM_URL = "https://registry.npmjs.org"

# Only support Plone 6+
MIN_PLONE_MAJOR = 6

CLIENT = httpx.Client(timeout=15, follow_redirects=True)


def _get_json(url: str) -> Any:
    """Fetch JSON from URL."""
    resp = CLIENT.get(url)
    resp.raise_for_status()
    return resp.json()


def _get_text(url: str) -> str:
    """Fetch text content from URL."""
    resp = CLIENT.get(url)
    resp.raise_for_status()
    return resp.text


def _parse_version(v: str) -> tuple:
    """Parse version string into comparable tuple.

    Handles: 6.1.4, 6.2.0a1, 6.2.0b2, 6.2.0rc1
    """
    # Split off pre-release suffix
    match = re.match(r"(\d+(?:\.\d+)*)(?:(a|b|rc)(\d+))?", v)
    if not match:
        return (0,)
    base = tuple(int(x) for x in match.group(1).split("."))
    pre = match.group(2)
    pre_num = int(match.group(3)) if match.group(3) else 0
    if pre is None:
        # Stable release sorts after pre-releases
        return base + (99, 0)
    pre_order = {"a": 0, "b": 1, "rc": 2}
    return base + (pre_order.get(pre, 0), pre_num)


@lru_cache
def fetch_plone_versions() -> dict[str, list[str]]:
    """Fetch available Plone versions from dist.plone.org.

    Returns dict mapping major.minor to sorted list of patch versions.
    Example: {"6.1": ["6.1.0", "6.1.1", ..., "6.1.4"], "6.2": ["6.2.0a1"]}
    """
    html = _get_text(DIST_PLONE_URL)
    # Parse directory listing: href="6.1.4/" or href="6.2.0a1/"
    pattern = re.compile(r'href="(\d+\.\d+\.\d+(?:(?:a|b|rc)\d+)?)/?"')
    all_versions = pattern.findall(html)

    groups: dict[str, list[str]] = {}
    for v in all_versions:
        parts = v.split(".")
        major = int(parts[0])
        if major < MIN_PLONE_MAJOR:
            continue
        minor_key = f"{parts[0]}.{parts[1]}"
        groups.setdefault(minor_key, []).append(v)

    # Sort each group
    for key in groups:
        groups[key].sort(key=_parse_version)

    return groups


def get_latest_plone_versions() -> list[tuple[str, str]]:
    """Get the latest version for each Plone major.minor series.

    Returns list of (major.minor, latest_version) tuples, sorted descending.
    """
    groups = fetch_plone_versions()
    result = []
    for minor_key, versions in sorted(groups.items(), reverse=True):
        result.append((minor_key, versions[-1]))
    return result


@lru_cache
def get_python_versions(plone_version: str) -> list[str]:
    """Get supported Python versions from Products.CMFPlone PyPI classifiers.

    Fetches the specific Plone release metadata and parses classifiers like:
        "Programming Language :: Python :: 3.12"
    """
    # Resolve to latest patch if only major.minor given
    if plone_version.count(".") == 1:
        groups = fetch_plone_versions()
        versions = groups.get(plone_version, [])
        if versions:
            plone_version = versions[-1]
        else:
            return ["3.12", "3.13"]  # fallback

    url = f"{PYPI_URL}/Products.CMFPlone/{plone_version}/json"
    try:
        data = _get_json(url)
    except httpx.HTTPStatusError:
        return ["3.12", "3.13"]  # fallback

    classifiers = data.get("info", {}).get("classifiers", [])
    py_versions = []
    for c in classifiers:
        match = re.match(r"Programming Language :: Python :: (3\.\d+)$", c)
        if match:
            py_versions.append(match.group(1))

    py_versions.sort(key=lambda v: int(v.split(".")[1]))
    return py_versions if py_versions else ["3.12", "3.13"]


@lru_cache
def fetch_volto_versions() -> dict[str, list[str]]:
    """Fetch available Volto versions from npm registry.

    Returns dict mapping major version to sorted list of versions.
    Example: {"18": ["18.30.0", "18.31.0", "18.32.1"], "19": ["19.0.0-alpha.26"]}
    """
    url = f"{NPM_URL}/@plone/volto"
    data = _get_json(url)

    dist_tags = data.get("dist-tags", {})
    versions_map = data.get("versions", {})

    # Collect latest stable per major + any tagged pre-release
    groups: dict[str, list[str]] = {}
    tagged = set(dist_tags.values())

    for v in versions_map:
        match = re.match(r"(\d+)\.", v)
        if not match:
            continue
        major = match.group(1)
        if int(major) < 17:
            continue

        is_prerelease = bool(re.search(r"(alpha|beta|rc)", v))

        # Include: stable versions, or pre-releases that are tagged
        if not is_prerelease or v in tagged:
            groups.setdefault(major, []).append(v)

    # Sort and keep only the last few per major to avoid huge lists
    for key in groups:
        groups[key].sort(key=_parse_version)
        # Keep last 5 stable + any pre-releases
        stable = [v for v in groups[key] if not re.search(r"(alpha|beta|rc)", v)]
        pre = [v for v in groups[key] if re.search(r"(alpha|beta|rc)", v)]
        groups[key] = stable[-5:] + pre

    return groups


def get_latest_volto_versions() -> list[tuple[str, str]]:
    """Get the latest version for each Volto major series.

    Returns list of (major, latest_version) tuples, sorted descending.
    """
    groups = fetch_volto_versions()
    result = []
    for major, versions in sorted(groups.items(), key=lambda x: int(x[0]), reverse=True):
        # Prefer latest stable; if no stable, use latest pre-release
        stable = [v for v in versions if not re.search(r"(alpha|beta|rc)", v)]
        latest = stable[-1] if stable else versions[-1]
        result.append((major, latest))
    return result


@lru_cache
def get_node_versions(volto_version: str) -> list[str]:
    """Get supported Node.js versions from @plone/volto's engines.node field.

    Parses semver ranges like "^20 || ^22" into major version numbers.
    """
    url = f"{NPM_URL}/@plone/volto/{volto_version}"
    try:
        data = _get_json(url)
    except httpx.HTTPStatusError:
        return ["20", "22"]  # fallback

    engines = data.get("engines", {})
    node_range = engines.get("node", "")

    if not node_range:
        return ["20", "22"]  # fallback

    # Parse major versions from patterns like "^20 || ^22", ">=18", "^20"
    majors = re.findall(r"(\d+)", node_range)
    # Deduplicate and sort
    unique = sorted(set(majors), key=int)
    return unique if unique else ["20", "22"]


def get_pnpm_version(volto_version: str) -> str:
    """Get pnpm version from @plone/volto's packageManager field.

    Falls back to "9" if not found.
    """
    url = f"{NPM_URL}/@plone/volto/{volto_version}"
    try:
        data = _get_json(url)
    except httpx.HTTPStatusError:
        return "9"

    pm = data.get("packageManager", "")
    match = re.match(r"pnpm@(\d+)", pm)
    return match.group(1) if match else "9"
