"""Tests for root Makefile template."""
import tempfile
from pathlib import Path

from helpers.generate import generate_project


def _makefile(extra_context=None):
    """Generate project and return root Makefile content."""
    ctx = {"organization": "testorg", "project_name": "testproject"}
    if extra_context:
        ctx.update(extra_context)
    with tempfile.TemporaryDirectory() as tmpdir:
        result = generate_project(ctx, output_dir=tmpdir)
        return (Path(result) / "Makefile").read_text()


def test_makefile_exists():
    """Root Makefile is generated."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = generate_project(
            {"organization": "testorg", "project_name": "testproject"},
            output_dir=tmpdir,
        )
        assert (Path(result) / "Makefile").exists()


def test_makefile_has_backend_proxy_targets():
    """Makefile has backend proxy targets."""
    content = _makefile()
    for target in [
        "backend-install",
        "backend-start",
        "backend-test",
        "backend-check",
        "backend-format",
        "backend-clean",
    ]:
        assert f".PHONY: {target}" in content


def test_makefile_has_frontend_proxy_targets():
    """Makefile has frontend proxy targets."""
    content = _makefile()
    for target in [
        "frontend-install",
        "frontend-start",
        "frontend-build",
        "frontend-test",
        "frontend-check",
        "frontend-format",
        "frontend-i18n",
        "frontend-storybook-start",
        "frontend-storybook-build",
        "frontend-clean",
    ]:
        assert f".PHONY: {target}" in content


def test_makefile_has_orchestration_targets():
    """Makefile has combined orchestration targets."""
    content = _makefile()
    for target in ["install", "check", "format", "test", "i18n", "clean"]:
        assert f".PHONY: {target}" in content


def test_makefile_has_docker_target():
    """Makefile has docker build target."""
    content = _makefile()
    assert "build-image" in content
    assert "docker build" in content


def test_makefile_has_correct_image():
    """Makefile uses correct container image from cookiecutter vars."""
    content = _makefile({"organization": "kup", "project_name": "tfv"})
    assert "ghcr.io/kup/kup-tfv" in content


def test_makefile_delegates_to_backend():
    """Makefile delegates to backend directory."""
    content = _makefile()
    assert "$(MAKE) -C backend" in content


def test_makefile_delegates_to_frontend():
    """Makefile delegates to frontend directory."""
    content = _makefile()
    assert "$(MAKE) -C frontend" in content


def test_makefile_help_is_default():
    """Help is the default target."""
    content = _makefile()
    assert ".DEFAULT_GOAL := help" in content
