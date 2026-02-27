"""Tests for helpers/create.py — Textual TUI."""
from unittest.mock import patch

import pytest

from textual.widgets import Button
from textual.widgets import Input
from textual.widgets import Select
from textual.widgets import Static


@pytest.fixture
def mock_versions():
    """Mock all version-fetching functions."""
    with (
        patch("helpers.versions.get_latest_plone_versions") as mock_plone,
        patch("helpers.versions.get_latest_volto_versions") as mock_volto,
        patch("helpers.versions.get_python_versions") as mock_python,
        patch("helpers.versions.get_node_versions") as mock_node,
        patch("helpers.versions.get_pnpm_version") as mock_pnpm,
    ):
        mock_plone.return_value = [("6.1", "6.1.4"), ("6.0", "6.0.11")]
        mock_volto.return_value = [("18", "18.32.1"), ("17", "17.1.0")]
        mock_python.return_value = ["3.11", "3.12", "3.13"]
        mock_node.return_value = ["20", "22"]
        mock_pnpm.return_value = "9"
        yield {
            "plone": mock_plone,
            "volto": mock_volto,
            "python": mock_python,
            "node": mock_node,
            "pnpm": mock_pnpm,
        }


@pytest.fixture
def app():
    from helpers.create import ZyklopenkekseCreateApp

    return ZyklopenkekseCreateApp()


async def test_app_starts(app, mock_versions):
    """App starts without error."""
    async with app.run_test() as pilot:
        assert app.title == "Zyklopenkekse - Create Plone Project"


async def test_app_has_all_input_fields(app, mock_versions):
    """All expected input fields are present."""
    async with app.run_test() as pilot:
        expected_inputs = [
            "organization",
            "project_name",
            "title",
            "author",
            "author_email",
            "initial_user_password",
            "container_registry",
        ]
        for field_id in expected_inputs:
            widget = app.query_one(f"#{field_id}", Input)
            assert widget is not None, f"Missing input: {field_id}"


async def test_app_has_all_select_fields(app, mock_versions):
    """All expected select fields are present."""
    async with app.run_test() as pilot:
        expected_selects = [
            "plone_version",
            "volto_version",
            "python_version",
            "node_version",
            "pnpm_version",
        ]
        for field_id in expected_selects:
            widget = app.query_one(f"#{field_id}", Select)
            assert widget is not None, f"Missing select: {field_id}"


async def test_app_has_buttons(app, mock_versions):
    """Create and Cancel buttons are present."""
    async with app.run_test() as pilot:
        create_btn = app.query_one("#create", Button)
        cancel_btn = app.query_one("#cancel", Button)
        assert create_btn is not None
        assert cancel_btn is not None


async def test_app_has_summary(app, mock_versions):
    """Summary section is present."""
    async with app.run_test() as pilot:
        summary = app.query_one("#summary", Static)
        assert summary is not None


async def test_default_input_values(app, mock_versions):
    """Inputs have correct default values."""
    async with app.run_test() as pilot:
        assert app.query_one("#organization", Input).value == "myorg"
        assert app.query_one("#project_name", Input).value == "myproject"
        assert app.query_one("#title", Input).value == "My Project"
        # Author/email default from git config, fallback to hardcoded
        assert app.query_one("#author", Input).value != ""
        assert app.query_one("#author_email", Input).value != ""
        assert app.query_one("#initial_user_password", Input).value == "admin"
        assert app.query_one("#container_registry", Input).value == "ghcr.io/myorg"


async def test_version_fetch_populates_selects(app, mock_versions):
    """Version fetching populates the Select widgets."""
    async with app.run_test() as pilot:
        # Wait for the worker to complete
        await app.workers.wait_for_complete()

        plone_select = app.query_one("#plone_version", Select)
        assert plone_select.value == "6.1.4"

        volto_select = app.query_one("#volto_version", Select)
        assert volto_select.value == "18.32.1"

        python_select = app.query_one("#python_version", Select)
        assert python_select.value == "3.13"

        node_select = app.query_one("#node_version", Select)
        assert node_select.value == "22"


async def test_organization_change_updates_registry(app, mock_versions):
    """Changing organization updates the container registry."""
    async with app.run_test() as pilot:
        org_input = app.query_one("#organization", Input)
        org_input.value = "kup"
        # Textual processes events asynchronously
        await pilot.pause()

        registry = app.query_one("#container_registry", Input)
        assert registry.value == "ghcr.io/kup"


async def test_summary_updates_on_input_change(app, mock_versions):
    """Summary updates when organization or project_name change."""
    async with app.run_test() as pilot:
        app.query_one("#organization", Input).value = "kup"
        app.query_one("#project_name", Input).value = "tfv"
        await pilot.pause()

        summary = app.query_one("#summary", Static)
        # Static stores content in name-mangled __content
        text = str(summary._Static__content)
        assert "kup-tfv" in text
        assert "kup.tfv" in text
        assert "volto-kup-tfv" in text


async def test_cancel_exits(app, mock_versions):
    """Clicking Cancel exits the app."""
    async with app.run_test() as pilot:
        await pilot.click("#cancel")
        assert app.return_value is None


async def test_create_collects_values(app, mock_versions):
    """Clicking Create collects form values and exits."""
    async with app.run_test() as pilot:
        await app.workers.wait_for_complete()

        app.query_one("#organization", Input).value = "kup"
        app.query_one("#project_name", Input).value = "tfv"
        await pilot.pause()

        await pilot.click("#create")

        result = app.return_value
        assert result is not None
        assert result["organization"] == "kup"
        assert result["project_name"] == "tfv"


async def test_collect_values_all_fields(app, mock_versions):
    """_collect_values returns all expected fields."""
    async with app.run_test() as pilot:
        await app.workers.wait_for_complete()

        values = app._collect_values()
        expected_keys = {
            "organization",
            "project_name",
            "title",
            "author",
            "author_email",
            "plone_version",
            "volto_version",
            "python_version",
            "node_version",
            "pnpm_version",
            "initial_user_password",
            "include_frontend",
            "storage_backend",
            "container_registry",
            "ci_platform",
            "include_varnish",
            "include_ingress",
            "include_cnpg",
        }
        assert set(values.keys()) == expected_keys


async def test_fallback_versions_on_error(mock_versions):
    """Fallback versions are set when fetching fails."""
    mock_versions["plone"].side_effect = Exception("Network error")

    from helpers.create import ZyklopenkekseCreateApp

    app = ZyklopenkekseCreateApp()
    async with app.run_test() as pilot:
        await app.workers.wait_for_complete()

        plone_select = app.query_one("#plone_version", Select)
        assert plone_select.value == "6.1"


async def test_plone_version_change_updates_python(app, mock_versions):
    """Changing Plone version updates Python version selector."""
    async with app.run_test() as pilot:
        await app.workers.wait_for_complete()

        # Change Python mock to return different versions for a different Plone
        mock_versions["python"].return_value = ["3.10", "3.11", "3.12"]

        plone_select = app.query_one("#plone_version", Select)
        plone_select.value = "6.0.11"
        await pilot.pause()
        await app.workers.wait_for_complete()

        # Python versions should have been re-fetched
        assert mock_versions["python"].call_count >= 2


async def test_volto_version_change_updates_node(app, mock_versions):
    """Changing Volto version updates Node version selector."""
    async with app.run_test() as pilot:
        await app.workers.wait_for_complete()

        mock_versions["node"].return_value = ["18", "20"]

        volto_select = app.query_one("#volto_version", Select)
        volto_select.value = "17.1.0"
        await pilot.pause()
        await app.workers.wait_for_complete()

        assert mock_versions["node"].call_count >= 2
