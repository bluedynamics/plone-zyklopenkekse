"""Test backend template content."""
import json

import yaml


def test_no_raw_cookiecutter_vars(cookies, default_context):
    """No unrendered {{ cookiecutter.* }} in output."""
    result = cookies.bake(extra_context=default_context)
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


def test_pyproject_has_correct_name(cookies):
    """pyproject.toml uses the derived package name."""
    result = cookies.bake(extra_context={
        "organization": "kup",
        "project_name": "tfv",
    })
    content = (result.project_path / "backend" / "pyproject.toml").read_text()
    assert 'name = "kup.tfv"' in content


def test_pyproject_has_correct_python(cookies):
    """pyproject.toml uses the specified Python version."""
    result = cookies.bake(extra_context={
        "organization": "testorg",
        "project_name": "testproject",
        "python_version": "3.12",
    })
    content = (result.project_path / "backend" / "pyproject.toml").read_text()
    assert 'requires-python = ">=3.12"' in content


def test_configure_zcml_distribution(cookies):
    """configure.zcml registers a plone.distribution."""
    result = cookies.bake(extra_context={
        "organization": "kup",
        "project_name": "tfv",
    })
    zcml = (
        result.project_path / "backend" / "src" / "kup" / "tfv" / "configure.zcml"
    ).read_text()
    assert 'name="kup.tfv"' in zcml
    assert 'directory="distributions/kup.tfv"' in zcml


def test_profiles_json(cookies):
    """Distribution profiles.json references the correct package profile."""
    result = cookies.bake(extra_context={
        "organization": "kup",
        "project_name": "tfv",
    })
    pj = json.loads(
        (
            result.project_path
            / "backend" / "src" / "kup" / "tfv"
            / "distributions" / "kup.tfv" / "profiles.json"
        ).read_text()
    )
    assert "kup.tfv:default" in pj["base"]


def test_browserlayer_xml(cookies):
    """browserlayer.xml uses correct interface path."""
    result = cookies.bake(extra_context={
        "organization": "kup",
        "project_name": "tfv",
    })
    bl = (
        result.project_path
        / "backend" / "src" / "kup" / "tfv"
        / "profiles" / "default" / "browserlayer.xml"
    ).read_text()
    assert "kup.tfv.interfaces.IBrowserLayer" in bl


def test_constraints_plone_version(cookies):
    """constraints.txt references correct Plone version."""
    result = cookies.bake(extra_context={
        "organization": "testorg",
        "project_name": "testproject",
        "plone_version": "6.1",
    })
    content = (result.project_path / "backend" / "constraints.txt").read_text()
    assert "6.1-dev" in content


def test_instance_yaml_password(cookies):
    """instance.yaml uses the configured password."""
    result = cookies.bake(extra_context={
        "organization": "testorg",
        "project_name": "testproject",
        "initial_user_password": "secret123",
    })
    content = (result.project_path / "backend" / "instance.yaml").read_text()
    assert "secret123" in content


def test_python_syntax_valid(cookies, default_context):
    """All generated .py files have valid syntax."""
    result = cookies.bake(extra_context=default_context)
    for py_file in result.project_path.rglob("*.py"):
        compile(py_file.read_text(), str(py_file), "exec")


def test_json_valid(cookies, default_context):
    """All generated .json files parse correctly."""
    result = cookies.bake(extra_context=default_context)
    for json_file in result.project_path.rglob("*.json"):
        if "node_modules" in str(json_file):
            continue
        json.loads(json_file.read_text())


def test_yaml_valid(cookies, default_context):
    """All generated .yaml files parse correctly."""
    result = cookies.bake(extra_context=default_context)
    for yaml_file in result.project_path.rglob("*.yaml"):
        yaml.safe_load(yaml_file.read_text())
