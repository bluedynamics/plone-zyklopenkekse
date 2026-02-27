"""Tests for helpers/versions.py — version fetching and parsing."""
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest


# --- _parse_version tests ---


def test_parse_version_stable():
    from helpers.versions import _parse_version

    assert _parse_version("6.1.4") > _parse_version("6.1.3")
    assert _parse_version("6.1.4") == _parse_version("6.1.4")


def test_parse_version_prerelease_order():
    from helpers.versions import _parse_version

    assert _parse_version("6.2.0a1") < _parse_version("6.2.0b1")
    assert _parse_version("6.2.0b1") < _parse_version("6.2.0rc1")
    assert _parse_version("6.2.0rc1") < _parse_version("6.2.0")


def test_parse_version_alpha_ordering():
    from helpers.versions import _parse_version

    assert _parse_version("6.2.0a1") < _parse_version("6.2.0a2")


def test_parse_version_stable_after_prerelease():
    from helpers.versions import _parse_version

    assert _parse_version("6.1.0") > _parse_version("6.1.0a1")
    assert _parse_version("6.1.0") > _parse_version("6.1.0rc1")


def test_parse_version_major_minor_compare():
    from helpers.versions import _parse_version

    assert _parse_version("6.2.0a1") > _parse_version("6.1.99")


def test_parse_version_invalid():
    from helpers.versions import _parse_version

    assert _parse_version("invalid") == (0,)


# --- fetch_plone_versions tests (mocked HTTP) ---


MOCK_DIST_PLONE_HTML = """
<!DOCTYPE html>
<html><body>
<a href="5.2.14/">5.2.14/</a>
<a href="6.0.0/">6.0.0/</a>
<a href="6.0.11/">6.0.11/</a>
<a href="6.1.0/">6.1.0/</a>
<a href="6.1.1/">6.1.1/</a>
<a href="6.1.4/">6.1.4/</a>
<a href="6.2.0a1/">6.2.0a1/</a>
<a href="6.2.0b2/">6.2.0b2/</a>
</body></html>
"""


@pytest.fixture(autouse=True)
def clear_caches():
    """Clear lru_cache between tests."""
    from helpers.versions import fetch_plone_versions
    from helpers.versions import fetch_volto_versions
    from helpers.versions import get_node_versions
    from helpers.versions import get_python_versions

    fetch_plone_versions.cache_clear()
    fetch_volto_versions.cache_clear()
    get_python_versions.cache_clear()
    get_node_versions.cache_clear()
    yield
    fetch_plone_versions.cache_clear()
    fetch_volto_versions.cache_clear()
    get_python_versions.cache_clear()
    get_node_versions.cache_clear()


@patch("helpers.versions._get_text")
def test_fetch_plone_versions(mock_get_text):
    from helpers.versions import fetch_plone_versions

    mock_get_text.return_value = MOCK_DIST_PLONE_HTML
    result = fetch_plone_versions()

    assert "6.1" in result
    assert "6.2" in result
    assert "6.0" in result
    # Plone 5 excluded
    assert "5.2" not in result


@patch("helpers.versions._get_text")
def test_fetch_plone_versions_sorted(mock_get_text):
    from helpers.versions import fetch_plone_versions

    mock_get_text.return_value = MOCK_DIST_PLONE_HTML
    result = fetch_plone_versions()

    # 6.1 versions sorted ascending
    assert result["6.1"] == ["6.1.0", "6.1.1", "6.1.4"]
    # 6.2 pre-releases sorted
    assert result["6.2"] == ["6.2.0a1", "6.2.0b2"]


@patch("helpers.versions._get_text")
def test_get_latest_plone_versions(mock_get_text):
    from helpers.versions import get_latest_plone_versions

    mock_get_text.return_value = MOCK_DIST_PLONE_HTML
    result = get_latest_plone_versions()

    # Returns list of (minor_key, latest) tuples, sorted descending
    keys = [k for k, _ in result]
    assert keys == ["6.2", "6.1", "6.0"]
    # Latest of 6.1 is 6.1.4
    latest_61 = dict(result)["6.1"]
    assert latest_61 == "6.1.4"
    # Latest of 6.2 is 6.2.0b2
    latest_62 = dict(result)["6.2"]
    assert latest_62 == "6.2.0b2"


# --- get_python_versions tests (mocked HTTP) ---


MOCK_PYPI_CMFPLONE = {
    "info": {
        "classifiers": [
            "Framework :: Plone :: 6.1",
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: 3.11",
            "Programming Language :: Python :: 3.12",
            "Programming Language :: Python :: 3.13",
        ]
    }
}


@patch("helpers.versions._get_json")
@patch("helpers.versions._get_text")
def test_get_python_versions_from_pypi(mock_get_text, mock_get_json):
    from helpers.versions import get_python_versions

    mock_get_text.return_value = MOCK_DIST_PLONE_HTML
    mock_get_json.return_value = MOCK_PYPI_CMFPLONE
    result = get_python_versions("6.1.4")

    assert result == ["3.10", "3.11", "3.12", "3.13"]


@patch("helpers.versions._get_json")
@patch("helpers.versions._get_text")
def test_get_python_versions_sorted(mock_get_text, mock_get_json):
    from helpers.versions import get_python_versions

    mock_get_text.return_value = MOCK_DIST_PLONE_HTML
    mock_get_json.return_value = MOCK_PYPI_CMFPLONE
    result = get_python_versions("6.1.4")

    # Should be sorted ascending by minor version
    minor_nums = [int(v.split(".")[1]) for v in result]
    assert minor_nums == sorted(minor_nums)


@patch("helpers.versions._get_json")
@patch("helpers.versions._get_text")
def test_get_python_versions_major_minor_resolves(mock_get_text, mock_get_json):
    """When given '6.1', resolves to latest patch and fetches that."""
    from helpers.versions import get_python_versions

    mock_get_text.return_value = MOCK_DIST_PLONE_HTML
    mock_get_json.return_value = MOCK_PYPI_CMFPLONE
    result = get_python_versions("6.1")

    # Should have called _get_json with 6.1.4 (latest of 6.1 series)
    mock_get_json.assert_called_with("https://pypi.org/pypi/Products.CMFPlone/6.1.4/json")
    assert "3.13" in result


@patch("helpers.versions._get_json")
@patch("helpers.versions._get_text")
def test_get_python_versions_fallback_on_error(mock_get_text, mock_get_json):
    import httpx

    from helpers.versions import get_python_versions

    mock_get_text.return_value = MOCK_DIST_PLONE_HTML
    mock_get_json.side_effect = httpx.HTTPStatusError(
        "404", request=MagicMock(), response=MagicMock()
    )
    result = get_python_versions("6.1.4")

    assert result == ["3.12", "3.13"]


@patch("helpers.versions._get_json")
@patch("helpers.versions._get_text")
def test_get_python_versions_fallback_no_classifiers(mock_get_text, mock_get_json):
    from helpers.versions import get_python_versions

    mock_get_text.return_value = MOCK_DIST_PLONE_HTML
    mock_get_json.return_value = {"info": {"classifiers": []}}
    result = get_python_versions("6.1.4")

    assert result == ["3.12", "3.13"]


# --- fetch_volto_versions tests (mocked HTTP) ---


MOCK_NPM_VOLTO = {
    "dist-tags": {
        "latest": "18.32.1",
        "alpha": "19.0.0-alpha.26",
    },
    "versions": {
        "17.0.0": {},
        "17.1.0": {},
        "18.30.0": {},
        "18.31.0": {},
        "18.32.0": {},
        "18.32.1": {},
        "19.0.0-alpha.25": {},
        "19.0.0-alpha.26": {},
    },
}


@patch("helpers.versions._get_json")
def test_fetch_volto_versions(mock_get_json):
    from helpers.versions import fetch_volto_versions

    mock_get_json.return_value = MOCK_NPM_VOLTO
    result = fetch_volto_versions()

    assert "18" in result
    assert "17" in result


@patch("helpers.versions._get_json")
def test_fetch_volto_versions_includes_tagged_prereleases(mock_get_json):
    from helpers.versions import fetch_volto_versions

    mock_get_json.return_value = MOCK_NPM_VOLTO
    result = fetch_volto_versions()

    # 19.0.0-alpha.26 is tagged (dist-tags.alpha), so included
    assert "19" in result
    assert "19.0.0-alpha.26" in result["19"]


@patch("helpers.versions._get_json")
def test_fetch_volto_versions_excludes_untagged_prereleases(mock_get_json):
    from helpers.versions import fetch_volto_versions

    mock_get_json.return_value = MOCK_NPM_VOLTO
    result = fetch_volto_versions()

    # 19.0.0-alpha.25 is NOT tagged, so excluded
    assert "19.0.0-alpha.25" not in result.get("19", [])


@patch("helpers.versions._get_json")
def test_get_latest_volto_versions(mock_get_json):
    from helpers.versions import get_latest_volto_versions

    mock_get_json.return_value = MOCK_NPM_VOLTO
    result = get_latest_volto_versions()

    result_dict = dict(result)
    # v19 only has alpha, so latest is the alpha
    assert result_dict["19"] == "19.0.0-alpha.26"
    # v18 has stable releases, so latest is stable
    assert result_dict["18"] == "18.32.1"


@patch("helpers.versions._get_json")
def test_get_latest_volto_versions_descending(mock_get_json):
    from helpers.versions import get_latest_volto_versions

    mock_get_json.return_value = MOCK_NPM_VOLTO
    result = get_latest_volto_versions()

    majors = [int(k) for k, _ in result]
    assert majors == sorted(majors, reverse=True)


# --- get_node_versions tests (mocked HTTP) ---


@patch("helpers.versions._get_json")
def test_get_node_versions_caret_range(mock_get_json):
    from helpers.versions import get_node_versions

    mock_get_json.return_value = {"engines": {"node": "^20 || ^22"}}
    result = get_node_versions("18.32.1")

    assert result == ["20", "22"]


@patch("helpers.versions._get_json")
def test_get_node_versions_gte_range(mock_get_json):
    from helpers.versions import get_node_versions

    mock_get_json.return_value = {"engines": {"node": ">=18"}}
    result = get_node_versions("18.32.1")

    assert "18" in result


@patch("helpers.versions._get_json")
def test_get_node_versions_no_engines(mock_get_json):
    from helpers.versions import get_node_versions

    mock_get_json.return_value = {}
    result = get_node_versions("18.32.1")

    assert result == ["20", "22"]  # fallback


@patch("helpers.versions._get_json")
def test_get_node_versions_empty_node(mock_get_json):
    from helpers.versions import get_node_versions

    mock_get_json.return_value = {"engines": {"node": ""}}
    result = get_node_versions("18.32.1")

    assert result == ["20", "22"]  # fallback


@patch("helpers.versions._get_json")
def test_get_node_versions_http_error(mock_get_json):
    import httpx

    from helpers.versions import get_node_versions

    mock_get_json.side_effect = httpx.HTTPStatusError(
        "404", request=MagicMock(), response=MagicMock()
    )
    result = get_node_versions("99.99.99")

    assert result == ["20", "22"]  # fallback


# --- get_pnpm_version tests ---


@patch("helpers.versions._get_json")
def test_get_pnpm_version(mock_get_json):
    from helpers.versions import get_pnpm_version

    mock_get_json.return_value = {"packageManager": "pnpm@9.15.0"}
    result = get_pnpm_version("18.32.1")

    assert result == "9"


@patch("helpers.versions._get_json")
def test_get_pnpm_version_v8(mock_get_json):
    from helpers.versions import get_pnpm_version

    mock_get_json.return_value = {"packageManager": "pnpm@8.6.0"}
    result = get_pnpm_version("17.0.0")

    assert result == "8"


@patch("helpers.versions._get_json")
def test_get_pnpm_version_no_field(mock_get_json):
    from helpers.versions import get_pnpm_version

    mock_get_json.return_value = {}
    result = get_pnpm_version("18.32.1")

    assert result == "9"  # fallback


@patch("helpers.versions._get_json")
def test_get_pnpm_version_http_error(mock_get_json):
    import httpx

    from helpers.versions import get_pnpm_version

    mock_get_json.side_effect = httpx.HTTPStatusError(
        "404", request=MagicMock(), response=MagicMock()
    )
    result = get_pnpm_version("99.99.99")

    assert result == "9"  # fallback


# --- Integration test (live network, skip in CI) ---


@pytest.mark.skipif(
    True, reason="Live network test — enable manually with: pytest -k test_live"
)
def test_live_fetch_plone_versions():
    from helpers.versions import fetch_plone_versions

    versions = fetch_plone_versions()
    assert "6.1" in versions
    assert len(versions["6.1"]) > 0


@pytest.mark.skipif(
    True, reason="Live network test — enable manually with: pytest -k test_live"
)
def test_live_fetch_volto_versions():
    from helpers.versions import fetch_volto_versions

    versions = fetch_volto_versions()
    assert "18" in versions
