"""Test Dockerfile and deployment template content."""


def test_dockerfile_uses_correct_python(cookies):
    """Dockerfile ARG uses the specified Python version."""
    result = cookies.bake(extra_context={
        "organization": "testorg",
        "project_name": "testproject",
        "python_version": "3.12",
    })
    content = (result.project_path / "Dockerfile").read_text()
    assert "PYTHON_VERSION=3.12" in content


def test_dockerfile_uses_correct_node(cookies):
    """Dockerfile ARG uses the specified Node version."""
    result = cookies.bake(extra_context={
        "organization": "testorg",
        "project_name": "testproject",
        "node_version": "20",
    })
    content = (result.project_path / "Dockerfile").read_text()
    assert "NODE_VERSION=20" in content


def test_dockerfile_label(cookies):
    """Dockerfile label includes project title."""
    result = cookies.bake(extra_context={
        "organization": "testorg",
        "project_name": "testproject",
        "title": "My Great Project",
    })
    content = (result.project_path / "Dockerfile").read_text()
    assert "My Great Project" in content


def test_dockerfile_deployment_paths(cookies, default_context):
    """Dockerfile uses /deployment/ not /backend/deployment/."""
    result = cookies.bake(extra_context=default_context)
    content = (result.project_path / "Dockerfile").read_text()
    assert "/deployment/entrypoint.sh" in content
    assert "/deployment/cookiecutter-zope-instance.zip" in content
    assert "/backend/deployment/" not in content


def test_entrypoint_references_deployment(cookies, default_context):
    """Entrypoint uses /deployment/ not /backend/deployment/."""
    result = cookies.bake(extra_context=default_context)
    content = (result.project_path / "deployment" / "entrypoint.sh").read_text()
    assert "/deployment/commands.d/" in content
    assert "/backend/deployment/" not in content


def test_entrypoint_has_all_commands(cookies, default_context):
    """Entrypoint supports all expected commands."""
    result = cookies.bake(extra_context=default_context)
    content = (result.project_path / "deployment" / "entrypoint.sh").read_text()
    for cmd in ["start-backend", "start-frontend", "export", "import", "pack"]:
        assert cmd in content, f"Missing command: {cmd}"


def test_dockerignore_exists(cookies, default_context):
    """Docker ignore file is present."""
    result = cookies.bake(extra_context=default_context)
    assert (result.project_path / ".dockerignore").exists()
