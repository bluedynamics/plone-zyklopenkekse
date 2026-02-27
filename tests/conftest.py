"""pytest-cookies fixtures for template testing."""
import pytest


@pytest.fixture
def default_context():
    """Default template context for testing."""
    return {
        "organization": "testorg",
        "project_name": "testproject",
        "title": "Test Project",
        "author": "Test Author",
        "author_email": "test@example.com",
        "plone_version": "6.1",
        "volto_version": "18.32.1",
        "python_version": "3.13",
        "node_version": "22",
        "pnpm_version": "9",
        "initial_user_password": "admin",
        "container_registry": "ghcr.io/testorg",
    }
