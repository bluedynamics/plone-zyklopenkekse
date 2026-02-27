"""Tests for CI pipeline templates."""
import tempfile
from pathlib import Path

from helpers.generate import generate_project


def test_github_ci_exists_by_default():
    """Default generation includes GitHub Actions CI."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = generate_project(
            {"organization": "testorg", "project_name": "testproject"},
            output_dir=tmpdir,
        )
        ci = Path(result) / ".github" / "workflows" / "ci.yml"
        assert ci.exists()


def test_github_ci_no_gitlab():
    """GitHub platform removes .gitlab-ci.yml."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = generate_project(
            {
                "organization": "testorg",
                "project_name": "testproject",
                "ci_platform": "github",
            },
            output_dir=tmpdir,
        )
        assert not (Path(result) / ".gitlab-ci.yml").exists()
        assert (Path(result) / ".github" / "workflows" / "ci.yml").exists()


def test_gitlab_ci_exists():
    """GitLab platform generates .gitlab-ci.yml."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = generate_project(
            {
                "organization": "testorg",
                "project_name": "testproject",
                "ci_platform": "gitlab",
            },
            output_dir=tmpdir,
        )
        assert (Path(result) / ".gitlab-ci.yml").exists()


def test_gitlab_ci_no_github():
    """GitLab platform removes .github/ directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = generate_project(
            {
                "organization": "testorg",
                "project_name": "testproject",
                "ci_platform": "gitlab",
            },
            output_dir=tmpdir,
        )
        assert not (Path(result) / ".github").exists()


def test_github_ci_has_check_job():
    """GitHub CI has check job."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = generate_project(
            {"organization": "testorg", "project_name": "testproject"},
            output_dir=tmpdir,
        )
        ci = (Path(result) / ".github" / "workflows" / "ci.yml").read_text()
        assert "check:" in ci
        assert "backend-check" in ci
        assert "frontend-check" in ci


def test_github_ci_has_test_job():
    """GitHub CI has test job."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = generate_project(
            {"organization": "testorg", "project_name": "testproject"},
            output_dir=tmpdir,
        )
        ci = (Path(result) / ".github" / "workflows" / "ci.yml").read_text()
        assert "test:" in ci
        assert "backend-test" in ci
        assert "frontend-test" in ci


def test_github_ci_has_build_image_job():
    """GitHub CI has build-image job with multi-arch."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = generate_project(
            {"organization": "testorg", "project_name": "testproject"},
            output_dir=tmpdir,
        )
        ci = (Path(result) / ".github" / "workflows" / "ci.yml").read_text()
        assert "build-image:" in ci
        assert "linux/amd64,linux/arm64" in ci


def test_github_ci_has_correct_image():
    """GitHub CI references correct container image."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = generate_project(
            {"organization": "kup", "project_name": "tfv"},
            output_dir=tmpdir,
        )
        ci = (Path(result) / ".github" / "workflows" / "ci.yml").read_text()
        assert "ghcr.io/kup/kup-tfv" in ci


def test_gitlab_ci_has_stages():
    """GitLab CI has lint, test, build stages."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = generate_project(
            {
                "organization": "testorg",
                "project_name": "testproject",
                "ci_platform": "gitlab",
            },
            output_dir=tmpdir,
        )
        ci = (Path(result) / ".gitlab-ci.yml").read_text()
        assert "lint" in ci
        assert "test" in ci
        assert "build" in ci


def test_gitlab_ci_has_multi_arch():
    """GitLab CI builds multi-arch images."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = generate_project(
            {
                "organization": "testorg",
                "project_name": "testproject",
                "ci_platform": "gitlab",
            },
            output_dir=tmpdir,
        )
        ci = (Path(result) / ".gitlab-ci.yml").read_text()
        assert "linux/amd64,linux/arm64" in ci


def test_gitlab_ci_has_python_version():
    """GitLab CI uses correct Python version."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = generate_project(
            {
                "organization": "testorg",
                "project_name": "testproject",
                "ci_platform": "gitlab",
                "python_version": "3.13",
            },
            output_dir=tmpdir,
        )
        ci = (Path(result) / ".gitlab-ci.yml").read_text()
        assert "python:3.13" in ci
