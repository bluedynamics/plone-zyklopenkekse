"""Tests for storage backend options."""
import tempfile
from pathlib import Path

import pytest

from helpers.generate import generate_project


def _generate_with_storage(backend, **extra):
    """Generate a project with a specific storage backend."""
    ctx = {
        "organization": "testorg",
        "project_name": "testproject",
        "storage_backend": backend,
    }
    ctx.update(extra)
    tmpdir = tempfile.mkdtemp()
    return Path(generate_project(ctx, output_dir=tmpdir))


@pytest.fixture(scope="module")
def relstorage_project():
    """Generate project with relstorage backend."""
    return _generate_with_storage("relstorage")


@pytest.fixture(scope="module")
def pgjsonb_project():
    """Generate project with pgjsonb backend."""
    return _generate_with_storage("pgjsonb")


@pytest.fixture(scope="module")
def none_project():
    """Generate project with no storage backend."""
    return _generate_with_storage("none")


# --- RelStorage tests ---


def test_relstorage_pyproject(relstorage_project):
    """RelStorage: pyproject.toml has relstorage deps."""
    content = (relstorage_project / "backend" / "pyproject.toml").read_text()
    assert "relstorage[postgresql]" in content
    assert "psycopg[binary]" in content
    assert "zodb-pgjsonb" not in content


def test_relstorage_dockerfile_env(relstorage_project):
    """RelStorage: Dockerfile has relstorage ENV vars."""
    content = (relstorage_project / "Dockerfile").read_text()
    assert "INSTANCE_db_storage=relstorage" in content
    assert "INSTANCE_db_relstorage=postgresql" in content
    assert "libpq-dev" in content
    assert "libpq5" in content


def test_relstorage_entrypoint(relstorage_project):
    """RelStorage: entrypoint has export/import/pack commands."""
    content = (relstorage_project / "deployment" / "entrypoint.sh").read_text()
    assert "relstorage-export.conf" in content
    assert "relstorage-import.conf" in content
    assert "relstorage-pack.conf" in content


def test_relstorage_cdk8s(relstorage_project):
    """RelStorage: cdk8s main.ts has relstorage env vars."""
    content = (relstorage_project / "deployment" / "cdk8s" / "main.ts").read_text()
    assert "INSTANCE_db_storage" in content
    assert "'relstorage'" in content
    assert "INSTANCE_db_relstorage_postgresql_dsn" in content


# --- PGJsonB tests ---


def test_pgjsonb_pyproject(pgjsonb_project):
    """PGJsonB: pyproject.toml has zodb-pgjsonb dep."""
    content = (pgjsonb_project / "backend" / "pyproject.toml").read_text()
    assert "zodb-pgjsonb" in content
    assert "relstorage" not in content


def test_pgjsonb_dockerfile_env(pgjsonb_project):
    """PGJsonB: Dockerfile has pgjsonb ENV vars."""
    content = (pgjsonb_project / "Dockerfile").read_text()
    assert "INSTANCE_db_storage=pgjsonb" in content
    assert "INSTANCE_db_blob_mode=cache" in content
    assert "relstorage" not in content.split("INSTANCE_db_storage=pgjsonb")[1]
    assert "libpq-dev" in content
    assert "libpq5" in content


def test_pgjsonb_entrypoint(pgjsonb_project):
    """PGJsonB: entrypoint has no export/import/pack commands."""
    content = (pgjsonb_project / "deployment" / "entrypoint.sh").read_text()
    assert "start-backend" in content
    assert "relstorage-export.conf" not in content
    assert "relstorage-import.conf" not in content
    assert "relstorage-pack.conf" not in content


def test_pgjsonb_cdk8s(pgjsonb_project):
    """PGJsonB: cdk8s main.ts has pgjsonb env vars."""
    content = (pgjsonb_project / "deployment" / "cdk8s" / "main.ts").read_text()
    assert "INSTANCE_db_storage" in content
    assert "'pgjsonb'" in content
    assert "INSTANCE_db_pgjsonb_dsn" in content
    assert "INSTANCE_db_relstorage" not in content


def test_pgjsonb_readme(pgjsonb_project):
    """PGJsonB: README mentions PGJsonB."""
    content = (pgjsonb_project / "README.md").read_text()
    assert "PGJsonB" in content


# --- None (custom) tests ---


def test_none_pyproject(none_project):
    """None: pyproject.toml has empty production extra."""
    content = (none_project / "backend" / "pyproject.toml").read_text()
    assert "relstorage" not in content
    assert "zodb-pgjsonb" not in content
    # production extra still exists but is empty
    assert "production" in content


def test_none_dockerfile_env(none_project):
    """None: Dockerfile has no storage ENV vars."""
    content = (none_project / "Dockerfile").read_text()
    assert "INSTANCE_db_storage" not in content
    assert "libpq-dev" not in content
    assert "libpq5" not in content


def test_none_entrypoint(none_project):
    """None: entrypoint has no export/import/pack commands."""
    content = (none_project / "deployment" / "entrypoint.sh").read_text()
    assert "start-backend" in content
    assert "relstorage-export.conf" not in content


def test_none_cdk8s(none_project):
    """None: cdk8s main.ts has comment placeholder."""
    content = (none_project / "deployment" / "cdk8s" / "main.ts").read_text()
    assert "Configure your database storage" in content
    assert "INSTANCE_db_relstorage" not in content
    assert "INSTANCE_db_pgjsonb_dsn" not in content
