"""Generate a project from the zyklopenkekse cookiecutter template."""
from __future__ import annotations

import os
from pathlib import Path

from cookiecutter.main import cookiecutter


TEMPLATE_DIR = str(Path(__file__).resolve().parent.parent)


def generate_project(context: dict, output_dir: str | None = None) -> str:
    """Generate a project using cookiecutter with the given context.

    Args:
        context: Dict of template variables (matching cookiecutter.json keys).
        output_dir: Where to create the project. Defaults to cwd.

    Returns:
        Path to the generated project directory.
    """
    if output_dir is None:
        output_dir = os.getcwd()

    result = cookiecutter(
        TEMPLATE_DIR,
        no_input=True,
        extra_context=context,
        output_dir=output_dir,
    )
    return result
