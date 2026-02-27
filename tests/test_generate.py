"""Tests for helpers/generate.py — project generation."""
import json
import tempfile
from pathlib import Path

from helpers.generate import TEMPLATE_DIR
from helpers.generate import generate_project


def test_template_dir_points_to_repo_root():
    """TEMPLATE_DIR points to the cyclop repo root."""
    assert Path(TEMPLATE_DIR).is_dir()
    assert (Path(TEMPLATE_DIR) / "cookiecutter.json").exists()


def test_generate_project_creates_directory():
    """generate_project creates a project directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = generate_project(
            {"organization": "testorg", "project_name": "testproject"},
            output_dir=tmpdir,
        )
        assert Path(result).is_dir()
        assert Path(result).name == "testorg-testproject"


def test_generate_project_has_backend():
    """Generated project has backend directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = generate_project(
            {"organization": "testorg", "project_name": "testproject"},
            output_dir=tmpdir,
        )
        assert (Path(result) / "backend").is_dir()
        assert (Path(result) / "backend" / "pyproject.toml").exists()


def test_generate_project_has_frontend():
    """Generated project has frontend directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = generate_project(
            {"organization": "testorg", "project_name": "testproject"},
            output_dir=tmpdir,
        )
        assert (Path(result) / "frontend").is_dir()
        assert (Path(result) / "frontend" / "package.json").exists()


def test_generate_project_has_deployment():
    """Generated project has deployment directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = generate_project(
            {"organization": "testorg", "project_name": "testproject"},
            output_dir=tmpdir,
        )
        assert (Path(result) / "deployment").is_dir()
        assert (Path(result) / "deployment" / "entrypoint.sh").exists()


def test_generate_project_renders_variables():
    """Generated project has variables rendered correctly."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = generate_project(
            {"organization": "kup", "project_name": "tfv"},
            output_dir=tmpdir,
        )
        pyproject = (Path(result) / "backend" / "pyproject.toml").read_text()
        assert 'name = "kup.tfv"' in pyproject


def test_generate_project_with_custom_versions():
    """Generated project uses custom version values."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = generate_project(
            {
                "organization": "test",
                "project_name": "proj",
                "python_version": "3.12",
                "node_version": "20",
                "volto_version": "18.30.0",
            },
            output_dir=tmpdir,
        )
        dockerfile = (Path(result) / "Dockerfile").read_text()
        assert "PYTHON_VERSION=3.12" in dockerfile
        assert "NODE_VERSION=20" in dockerfile

        mrs = json.loads(
            (Path(result) / "frontend" / "mrs.developer.json").read_text()
        )
        assert mrs["core"]["tag"] == "18.30.0"


def test_generate_project_namespace_package():
    """Generated project has correct namespace package structure."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = generate_project(
            {"organization": "kup", "project_name": "tfv"},
            output_dir=tmpdir,
        )
        pkg_dir = Path(result) / "backend" / "src" / "kup" / "tfv"
        assert pkg_dir.is_dir()
        assert (pkg_dir / "__init__.py").exists()
        assert (pkg_dir / "configure.zcml").exists()
        # Namespace level should NOT have __init__.py
        ns_dir = Path(result) / "backend" / "src" / "kup"
        assert not (ns_dir / "__init__.py").exists()


def test_generate_project_addon_package():
    """Generated project has correct Volto addon package."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = generate_project(
            {"organization": "kup", "project_name": "tfv"},
            output_dir=tmpdir,
        )
        addon_dir = Path(result) / "frontend" / "packages" / "volto-kup-tfv"
        assert addon_dir.is_dir()
        pkg_json = json.loads((addon_dir / "package.json").read_text())
        assert pkg_json["name"] == "volto-kup-tfv"


def test_generate_project_distribution():
    """Generated project has plone.distribution scaffold."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = generate_project(
            {"organization": "kup", "project_name": "tfv"},
            output_dir=tmpdir,
        )
        dist_dir = (
            Path(result) / "backend" / "src" / "kup" / "tfv"
            / "distributions" / "kup.tfv"
        )
        assert dist_dir.is_dir()
        assert (dist_dir / "profiles.json").exists()
        assert (dist_dir / "image.png").exists()
        assert (dist_dir / "content" / "__metadata__.json").exists()


def test_generate_project_entrypoint_executable():
    """Generated entrypoint.sh is executable."""
    import os
    import stat

    with tempfile.TemporaryDirectory() as tmpdir:
        result = generate_project(
            {"organization": "testorg", "project_name": "testproject"},
            output_dir=tmpdir,
        )
        entrypoint = Path(result) / "deployment" / "entrypoint.sh"
        mode = os.stat(entrypoint).st_mode
        assert mode & stat.S_IXUSR, "entrypoint.sh should be executable"
