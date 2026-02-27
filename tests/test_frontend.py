"""Test frontend template content."""
import json


def test_package_json_addon_name(cookies):
    """package.json references the correct addon."""
    result = cookies.bake(extra_context={
        "organization": "kup",
        "project_name": "tfv",
    })
    pkg = json.loads(
        (result.project_path / "frontend" / "package.json").read_text()
    )
    assert "volto-kup-tfv" in pkg["dependencies"]


def test_package_json_name(cookies):
    """package.json uses correct dev project name."""
    result = cookies.bake(extra_context={
        "organization": "kup",
        "project_name": "tfv",
    })
    pkg = json.loads(
        (result.project_path / "frontend" / "package.json").read_text()
    )
    assert pkg["name"] == "volto-kup-tfv-dev"


def test_addon_package_exists(cookies):
    """Volto addon package directory is created."""
    result = cookies.bake(extra_context={
        "organization": "kup",
        "project_name": "tfv",
    })
    addon_dir = result.project_path / "frontend" / "packages" / "volto-kup-tfv"
    assert addon_dir.is_dir()
    assert (addon_dir / "package.json").exists()
    assert (addon_dir / "src" / "index.ts").exists()


def test_addon_package_json(cookies):
    """Addon package.json has correct name."""
    result = cookies.bake(extra_context={
        "organization": "kup",
        "project_name": "tfv",
    })
    addon_pkg = json.loads(
        (
            result.project_path / "frontend" / "packages"
            / "volto-kup-tfv" / "package.json"
        ).read_text()
    )
    assert addon_pkg["name"] == "volto-kup-tfv"


def test_volto_version_in_mrs_developer(cookies):
    """mrs.developer.json pins the correct Volto version."""
    result = cookies.bake(extra_context={
        "organization": "testorg",
        "project_name": "testproject",
        "volto_version": "18.30.0",
    })
    mrs = json.loads(
        (result.project_path / "frontend" / "mrs.developer.json").read_text()
    )
    assert mrs["core"]["tag"] == "18.30.0"


def test_volto_config_addon(cookies):
    """volto.config.js references the correct addon."""
    result = cookies.bake(extra_context={
        "organization": "kup",
        "project_name": "tfv",
    })
    content = (result.project_path / "frontend" / "volto.config.js").read_text()
    assert "volto-kup-tfv" in content


def test_pnpm_version_in_package_json(cookies):
    """package.json has correct pnpm version in packageManager."""
    result = cookies.bake(extra_context={
        "organization": "testorg",
        "project_name": "testproject",
        "pnpm_version": "9",
    })
    pkg = json.loads(
        (result.project_path / "frontend" / "package.json").read_text()
    )
    assert pkg["packageManager"] == "pnpm@9"


def test_storybook_files_exist(cookies, default_context):
    """Storybook config files are present."""
    result = cookies.bake(extra_context=default_context)
    p = result.project_path / "frontend"
    assert (p / ".storybook" / "main.js").exists()
    assert (p / ".storybook" / "preview.jsx").exists()


def test_cypress_files_exist(cookies, default_context):
    """Cypress test files are present."""
    result = cookies.bake(extra_context=default_context)
    p = result.project_path / "frontend"
    assert (p / "cypress" / "tsconfig.json").exists()
    assert (p / "cypress" / "tests" / "example.cy.js").exists()
    assert (p / "cypress" / "support" / "commands.js").exists()
    assert (p / "cypress" / "support" / "e2e.js").exists()
    assert (p / "cypress" / "support" / "index.ts").exists()


def test_frontend_preseed(cookies):
    """Frontend preseed references correct addon name."""
    result = cookies.bake(extra_context={
        "organization": "kup",
        "project_name": "tfv",
    })
    content = (result.project_path / "frontend" / "mxmake-preseed.yaml").read_text()
    assert "volto-kup-tfv" in content
