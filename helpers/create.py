"""Zyklopenkekse TUI — interactive project creation with Textual."""
from __future__ import annotations

import subprocess

from textual.app import App
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.containers import VerticalScroll
from textual.widgets import Button
from textual.widgets import Footer
from textual.widgets import Header
from textual.widgets import Input
from textual.widgets import Select
from textual.widgets import Static
from textual.widgets import Switch


def _git_config(key: str, fallback: str = "") -> str:
    """Read a value from git config, return fallback if unavailable."""
    try:
        result = subprocess.run(
            ["git", "config", key],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return fallback


class ZyklopenkekseCreateApp(App):
    """Textual app for creating Plone projects."""

    TITLE = "Zyklopenkekse - Create Plone Project"
    CSS = """
    Screen {
        layout: vertical;
    }
    #form {
        padding: 1 2;
    }
    .form-row {
        height: 3;
        margin-bottom: 1;
    }
    .form-label {
        width: 20;
        content-align: right middle;
        padding-right: 1;
    }
    .form-input {
        width: 1fr;
    }
    .section-label {
        margin-top: 1;
        margin-bottom: 0;
        padding: 0 2;
        text-style: bold;
    }
    .switch-row {
        height: 3;
        margin-bottom: 0;
    }
    .switch-label {
        width: 30;
        content-align: left middle;
        padding-left: 4;
    }
    #summary {
        margin: 1 2;
        padding: 1 2;
        border: round $accent;
        height: auto;
    }
    #buttons {
        height: 3;
        margin: 1 2;
        align: center middle;
    }
    #buttons Button {
        margin: 0 2;
    }
    """

    def __init__(self):
        super().__init__()
        self._plone_versions: list[tuple[str, str]] = []
        self._volto_versions: list[tuple[str, str]] = []
        self._python_versions: list[str] = []
        self._node_versions: list[str] = []
        self._result: dict | None = None

    def compose(self) -> ComposeResult:
        yield Header()
        with VerticalScroll(id="form"):
            with Horizontal(classes="form-row"):
                yield Static("Organization", classes="form-label")
                yield Input(
                    value="myorg",
                    placeholder="Organization (e.g. kup, akbild)",
                    id="organization",
                    classes="form-input",
                )
            with Horizontal(classes="form-row"):
                yield Static("Project Name", classes="form-label")
                yield Input(
                    value="myproject",
                    placeholder="Project name (e.g. tfv, portal)",
                    id="project_name",
                    classes="form-input",
                )
            with Horizontal(classes="form-row"):
                yield Static("Title", classes="form-label")
                yield Input(
                    value="My Project",
                    placeholder="Human-readable title",
                    id="title",
                    classes="form-input",
                )
            with Horizontal(classes="switch-row"):
                yield Static("Include Frontend (Volto)", classes="switch-label")
                yield Switch(value=True, id="include_frontend")
            with Horizontal(classes="form-row"):
                yield Static("Plone Version", classes="form-label")
                yield Select(
                    [("Loading...", "loading")],
                    id="plone_version",
                    classes="form-input",
                )
            with Horizontal(classes="form-row"):
                yield Static("Volto Version", classes="form-label")
                yield Select(
                    [("Loading...", "loading")],
                    id="volto_version",
                    classes="form-input",
                )
            with Horizontal(classes="form-row"):
                yield Static("Python", classes="form-label")
                yield Select(
                    [("Loading...", "loading")],
                    id="python_version",
                    classes="form-input",
                )
            with Horizontal(classes="form-row"):
                yield Static("Node.js", classes="form-label")
                yield Select(
                    [("Loading...", "loading")],
                    id="node_version",
                    classes="form-input",
                )
            with Horizontal(classes="form-row"):
                yield Static("pnpm", classes="form-label")
                yield Select(
                    [("9", "9"), ("8", "8")],
                    value="9",
                    id="pnpm_version",
                    classes="form-input",
                )
            with Horizontal(classes="form-row"):
                yield Static("Author", classes="form-label")
                yield Input(
                    value=_git_config("user.name", "John Doe"),
                    placeholder="Author name",
                    id="author",
                    classes="form-input",
                )
            with Horizontal(classes="form-row"):
                yield Static("Email", classes="form-label")
                yield Input(
                    value=_git_config("user.email", "john@example.com"),
                    placeholder="Author email",
                    id="author_email",
                    classes="form-input",
                )
            with Horizontal(classes="form-row"):
                yield Static("Admin Password", classes="form-label")
                yield Input(
                    value="admin",
                    placeholder="Initial admin password",
                    id="initial_user_password",
                    classes="form-input",
                )
            with Horizontal(classes="form-row"):
                yield Static("Registry", classes="form-label")
                yield Input(
                    value="ghcr.io/myorg",
                    placeholder="Container registry",
                    id="container_registry",
                    classes="form-input",
                )
            with Horizontal(classes="form-row"):
                yield Static("Storage Backend", classes="form-label")
                yield Select(
                    [
                        ("PGJsonB", "pgjsonb"),
                        ("RelStorage (PostgreSQL)", "relstorage"),
                        ("None (custom)", "none"),
                    ],
                    value="pgjsonb",
                    id="storage_backend",
                    classes="form-input",
                )
            with Horizontal(classes="form-row"):
                yield Static("CI Platform", classes="form-label")
                yield Select(
                    [("GitHub Actions", "github"), ("GitLab CI", "gitlab")],
                    value="github",
                    id="ci_platform",
                    classes="form-input",
                )
            yield Static("Deployment Options", classes="section-label")
            with Horizontal(classes="switch-row"):
                yield Static("Include Varnish (HTTP cache)", classes="switch-label")
                yield Switch(value=True, id="include_varnish")
            with Horizontal(classes="switch-row"):
                yield Static("Include Ingress", classes="switch-label")
                yield Switch(value=True, id="include_ingress")
            with Horizontal(classes="switch-row"):
                yield Static("Include CloudNativePG", classes="switch-label")
                yield Switch(value=True, id="include_cnpg")
        yield Static(id="summary")
        with Horizontal(id="buttons"):
            yield Button("Create Project", variant="primary", id="create")
            yield Button("Cancel", variant="error", id="cancel")
        yield Footer()

    async def on_mount(self) -> None:
        """Fetch versions in background on startup."""
        self.run_worker(self._fetch_versions)

    async def _fetch_versions(self) -> None:
        """Fetch Plone and Volto versions from remote sources."""
        from .versions import get_latest_plone_versions
        from .versions import get_latest_volto_versions
        from .versions import get_node_versions
        from .versions import get_pnpm_version
        from .versions import get_python_versions

        try:
            # Plone versions
            plone_versions = get_latest_plone_versions()
            self._plone_versions = plone_versions
            plone_select = self.query_one("#plone_version", Select)
            options = [(f"{v} ({k})", v) for k, v in plone_versions]
            plone_select.set_options(options)
            if options:
                plone_select.value = options[0][1]

            # Volto versions
            volto_versions = get_latest_volto_versions()
            self._volto_versions = volto_versions
            volto_select = self.query_one("#volto_version", Select)
            options = [(f"{v} (v{k})", v) for k, v in volto_versions]
            volto_select.set_options(options)
            if options:
                volto_select.value = options[0][1]

            # Python versions (based on latest Plone)
            if plone_versions:
                latest_plone = plone_versions[0][1]
                py_versions = get_python_versions(latest_plone)
                self._python_versions = py_versions
                py_select = self.query_one("#python_version", Select)
                options = [(v, v) for v in reversed(py_versions)]
                py_select.set_options(options)
                if options:
                    py_select.value = options[0][1]

            # Node versions (based on latest Volto)
            if volto_versions:
                latest_volto = volto_versions[0][1]
                node_versions = get_node_versions(latest_volto)
                self._node_versions = node_versions
                node_select = self.query_one("#node_version", Select)
                options = [(v, v) for v in reversed(node_versions)]
                node_select.set_options(options)
                if options:
                    node_select.value = options[0][1]

                # pnpm version
                pnpm = get_pnpm_version(latest_volto)
                pnpm_select = self.query_one("#pnpm_version", Select)
                pnpm_select.value = pnpm

        except Exception as e:
            self.notify(f"Version fetch failed: {e}", severity="warning")
            self._set_fallback_versions()

        self._update_summary()

    def _set_fallback_versions(self) -> None:
        """Set fallback values if remote fetching fails."""
        plone_select = self.query_one("#plone_version", Select)
        plone_select.set_options([("6.1", "6.1")])
        plone_select.value = "6.1"

        volto_select = self.query_one("#volto_version", Select)
        volto_select.set_options([("18.32.1", "18.32.1")])
        volto_select.value = "18.32.1"

        py_select = self.query_one("#python_version", Select)
        py_select.set_options([("3.13", "3.13"), ("3.12", "3.12")])
        py_select.value = "3.13"

        node_select = self.query_one("#node_version", Select)
        node_select.set_options([("22", "22"), ("20", "20")])
        node_select.value = "22"

    def on_input_changed(self, event: Input.Changed) -> None:
        """Update auto-derived fields when inputs change."""
        if event.input.id == "organization":
            registry = self.query_one("#container_registry", Input)
            registry.value = f"ghcr.io/{event.value}"
        self._update_summary()

    def on_select_changed(self, event: Select.Changed) -> None:
        """Update dependent versions when Plone/Volto selection changes."""
        if event.select.id == "plone_version" and event.value != "loading":
            self.run_worker(self._update_python_versions(str(event.value)))
        elif event.select.id == "volto_version" and event.value != "loading":
            self.run_worker(self._update_node_versions(str(event.value)))
        self._update_summary()

    async def _update_python_versions(self, plone_version: str) -> None:
        """Update Python version selector when Plone version changes."""
        from .versions import get_python_versions

        try:
            py_versions = get_python_versions(plone_version)
            self._python_versions = py_versions
            py_select = self.query_one("#python_version", Select)
            options = [(v, v) for v in reversed(py_versions)]
            py_select.set_options(options)
            if options:
                py_select.value = options[0][1]
        except Exception:
            pass

    async def _update_node_versions(self, volto_version: str) -> None:
        """Update Node.js version selector when Volto version changes."""
        from .versions import get_node_versions
        from .versions import get_pnpm_version

        try:
            node_versions = get_node_versions(volto_version)
            self._node_versions = node_versions
            node_select = self.query_one("#node_version", Select)
            options = [(v, v) for v in reversed(node_versions)]
            node_select.set_options(options)
            if options:
                node_select.value = options[0][1]

            pnpm = get_pnpm_version(volto_version)
            pnpm_select = self.query_one("#pnpm_version", Select)
            pnpm_select.value = pnpm
        except Exception:
            pass

    def _update_summary(self) -> None:
        """Update the summary display with derived values."""
        org = self.query_one("#organization", Input).value
        proj = self.query_one("#project_name", Input).value
        include_frontend = self.query_one("#include_frontend", Switch).value
        summary = self.query_one("#summary", Static)
        lines = [
            f"  Output: {org}-{proj}/",
            f"  Package: {org}.{proj}",
        ]
        if include_frontend:
            lines.append(f"  Addon: volto-{org}-{proj}")
        else:
            lines.append("  Mode: ClassicUI (no Volto frontend)")
        summary.update("\n".join(lines))

    def _collect_values(self) -> dict:
        """Collect all form values into a cookiecutter context dict."""
        def _get_input(id: str) -> str:
            return self.query_one(f"#{id}", Input).value

        def _get_select(id: str) -> str:
            val = self.query_one(f"#{id}", Select).value
            return str(val) if val else ""

        def _get_switch(id: str) -> str:
            return "yes" if self.query_one(f"#{id}", Switch).value else "no"

        return {
            "organization": _get_input("organization"),
            "project_name": _get_input("project_name"),
            "title": _get_input("title"),
            "author": _get_input("author"),
            "author_email": _get_input("author_email"),
            "plone_version": _get_select("plone_version"),
            "volto_version": _get_select("volto_version"),
            "python_version": _get_select("python_version"),
            "node_version": _get_select("node_version"),
            "pnpm_version": _get_select("pnpm_version"),
            "initial_user_password": _get_input("initial_user_password"),
            "include_frontend": _get_switch("include_frontend"),
            "storage_backend": _get_select("storage_backend"),
            "container_registry": _get_input("container_registry"),
            "ci_platform": _get_select("ci_platform"),
            "include_varnish": _get_switch("include_varnish"),
            "include_ingress": _get_switch("include_ingress"),
            "include_cnpg": _get_switch("include_cnpg"),
        }

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks."""
        if event.button.id == "cancel":
            self.exit()
        elif event.button.id == "create":
            values = self._collect_values()
            self._result = values
            self.exit(values)


def main():
    """Entry point for zyklopenkekse CLI."""
    app = ZyklopenkekseCreateApp()
    result = app.run()
    if result:
        from .generate import generate_project

        generate_project(result)


if __name__ == "__main__":
    main()
