"""Tests for ClassicUI-only mode (include_frontend=no)."""
import tempfile
from pathlib import Path

import pytest

from helpers.generate import generate_project


@pytest.fixture(scope="module")
def no_frontend_project():
    """Generate a no-frontend project once, reuse across tests."""
    ctx = {
        "organization": "testorg",
        "project_name": "testproject",
        "include_frontend": "no",
    }
    tmpdir = tempfile.mkdtemp()
    return Path(generate_project(ctx, output_dir=tmpdir))


@pytest.fixture(scope="module")
def no_frontend_github_project():
    """Generate a no-frontend project with GitHub CI."""
    ctx = {
        "organization": "testorg",
        "project_name": "testproject",
        "include_frontend": "no",
        "ci_platform": "github",
    }
    tmpdir = tempfile.mkdtemp()
    return Path(generate_project(ctx, output_dir=tmpdir))


@pytest.fixture(scope="module")
def no_frontend_gitlab_project():
    """Generate a no-frontend project with GitLab CI."""
    ctx = {
        "organization": "testorg",
        "project_name": "testproject",
        "include_frontend": "no",
        "ci_platform": "gitlab",
    }
    tmpdir = tempfile.mkdtemp()
    return Path(generate_project(ctx, output_dir=tmpdir))


def test_no_frontend_directory(no_frontend_project):
    """No frontend/ directory when include_frontend=no."""
    assert not (no_frontend_project / "frontend").exists()


def test_backend_exists(no_frontend_project):
    """Backend directory still exists without frontend."""
    assert (no_frontend_project / "backend").is_dir()
    assert (no_frontend_project / "backend" / "pyproject.toml").exists()


def test_backend_no_plone_volto_dep(no_frontend_project):
    """Backend pyproject.toml has no plone.volto dependency."""
    content = (no_frontend_project / "backend" / "pyproject.toml").read_text()
    assert "plone.volto" not in content
    assert "plone.distribution" in content


def test_configure_zcml_no_plone_volto(no_frontend_project):
    """configure.zcml does not include plone.volto."""
    zcml = (
        no_frontend_project / "backend" / "src" / "testorg" / "testproject" / "configure.zcml"
    ).read_text()
    assert "plone.volto" not in zcml
    assert "plone.distribution" in zcml


def test_metadata_xml_no_volto_dependency(no_frontend_project):
    """Default profile metadata.xml has no plone.volto dependency."""
    metadata = (
        no_frontend_project / "backend" / "src" / "testorg" / "testproject"
        / "profiles" / "default" / "metadata.xml"
    ).read_text()
    assert "plone.volto" not in metadata


def test_makefile_no_frontend_targets(no_frontend_project):
    """Root Makefile has no frontend targets."""
    content = (no_frontend_project / "Makefile").read_text()
    assert "frontend-install" not in content
    assert "frontend-start" not in content
    assert "frontend-test" not in content
    assert "$(MAKE) -C frontend" not in content
    # Backend targets still present
    assert "backend-install" in content
    assert "$(MAKE) -C backend" in content


def test_makefile_no_i18n_target(no_frontend_project):
    """Root Makefile has no i18n target without frontend."""
    content = (no_frontend_project / "Makefile").read_text()
    assert "i18n" not in content


def test_dockerfile_no_frontend_stage(no_frontend_project):
    """Dockerfile has no frontend-build stage."""
    content = (no_frontend_project / "Dockerfile").read_text()
    assert "frontend-build" not in content
    assert "FROM node:" not in content


def test_dockerfile_backend_only_expose(no_frontend_project):
    """Dockerfile only exposes port 8080."""
    content = (no_frontend_project / "Dockerfile").read_text()
    assert "EXPOSE 8080" in content
    assert "3000" not in content


def test_github_ci_no_frontend_jobs(no_frontend_github_project):
    """GitHub CI has no frontend steps."""
    ci = (no_frontend_github_project / ".github" / "workflows" / "ci.yml").read_text()
    assert "backend-check" in ci
    assert "frontend-check" not in ci
    assert "frontend-test" not in ci
    assert "setup-node" not in ci


def test_gitlab_ci_no_frontend_jobs(no_frontend_gitlab_project):
    """GitLab CI has no frontend jobs."""
    ci = (no_frontend_gitlab_project / ".gitlab-ci.yml").read_text()
    assert "lint-backend" in ci
    assert "lint-frontend" not in ci
    assert "test-frontend" not in ci


def test_cdk8s_no_frontend_pod(no_frontend_project):
    """cdk8s main.ts has no frontend pod definition."""
    content = (no_frontend_project / "deployment" / "cdk8s" / "main.ts").read_text()
    assert "start-backend" in content
    assert "start-frontend" not in content
    assert "FRONTEND_REPLICAS" not in content


def test_cdk8s_env_no_frontend_replicas(no_frontend_project):
    """cdk8s .env.example has no FRONTEND_REPLICAS."""
    content = (no_frontend_project / "deployment" / "cdk8s" / ".env.example").read_text()
    assert "BACKEND_REPLICAS" in content
    assert "FRONTEND_REPLICAS" not in content


def test_readme_classicui(no_frontend_project):
    """Root README mentions ClassicUI, not Volto."""
    content = (no_frontend_project / "README.md").read_text()
    assert "ClassicUI" in content
    assert "Volto" not in content
    assert "frontend-start" not in content


def test_gitignore_no_node_modules(no_frontend_project):
    """.gitignore has no node_modules entry."""
    content = (no_frontend_project / ".gitignore").read_text()
    assert "node_modules" not in content


def test_entrypoint_no_start_frontend(no_frontend_project):
    """Entrypoint has no start-frontend command."""
    content = (no_frontend_project / "deployment" / "entrypoint.sh").read_text()
    assert "start-backend" in content
    assert "start-frontend" not in content


def test_no_raw_cookiecutter_vars(cookies, no_frontend_context):
    """No unrendered {{ cookiecutter.* }} in no-frontend output."""
    result = cookies.bake(extra_context=no_frontend_context)
    for path in result.project_path.rglob("*"):
        if path.is_file() and path.suffix in (
            ".py", ".toml", ".json", ".xml", ".js", ".ts", ".yaml", ".yml",
        ):
            try:
                content = path.read_text()
            except UnicodeDecodeError:
                continue
            assert "{{ cookiecutter." not in content, (
                f"Unrendered variable in {path.relative_to(result.project_path)}"
            )
