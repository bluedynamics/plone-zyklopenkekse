"""Test template generation."""


def test_default_generation(cookies, default_context):
    """Template generates with default values."""
    result = cookies.bake(extra_context=default_context)
    assert result.exit_code == 0
    assert result.exception is None
    assert result.project_path.is_dir()


def test_custom_organization(cookies):
    """Template works with custom org/project names."""
    result = cookies.bake(extra_context={
        "organization": "kup",
        "project_name": "tfv",
    })
    assert result.exit_code == 0
    assert (result.project_path / "backend").is_dir()
    assert (result.project_path / "frontend").is_dir()
    assert (result.project_path / "deployment").is_dir()


def test_target_directory_name(cookies):
    """Generated directory uses org-project naming."""
    result = cookies.bake(extra_context={
        "organization": "kup",
        "project_name": "tfv",
    })
    assert result.project_path.name == "kup-tfv"


def test_expected_files_exist(cookies, default_context):
    """All expected files are generated."""
    result = cookies.bake(extra_context=default_context)
    p = result.project_path
    expected = [
        "Dockerfile",
        ".dockerignore",
        ".gitignore",
        "deployment/entrypoint.sh",
        "deployment/commands.d/.gitkeep",
        "backend/mx.ini",
        "backend/pyproject.toml",
        "backend/requirements.txt",
        "backend/constraints.txt",
        "backend/instance.yaml",
        "backend/include.mk",
        "backend/mxmake-preseed.yaml",
        "backend/tests/conftest.py",
        "frontend/package.json",
        "frontend/pnpm-workspace.yaml",
        "frontend/mrs.developer.json",
        "frontend/volto.config.js",
        "frontend/jest-addon.config.js",
        "frontend/cypress.config.js",
        "frontend/mxmake-preseed.yaml",
    ]
    for f in expected:
        assert (p / f).exists(), f"Missing: {f}"
