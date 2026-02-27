"""Tests for deployment/cdk8s template files."""
import json
import tempfile
from pathlib import Path

from helpers.generate import generate_project


def test_cdk8s_files_exist():
    """Generated project has cdk8s deployment files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = generate_project(
            {"organization": "testorg", "project_name": "testproject"},
            output_dir=tmpdir,
        )
        cdk8s = Path(result) / "deployment" / "cdk8s"
        assert cdk8s.is_dir()
        assert (cdk8s / "main.ts").exists()
        assert (cdk8s / "package.json").exists()
        assert (cdk8s / "cdk8s.yaml").exists()
        assert (cdk8s / "tsconfig.json").exists()
        assert (cdk8s / ".env.example").exists()
        assert (cdk8s / ".gitignore").exists()
        assert (cdk8s / "dist").is_dir()


def test_cdk8s_package_json_name():
    """package.json has correct project name."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = generate_project(
            {"organization": "kup", "project_name": "tfv"},
            output_dir=tmpdir,
        )
        pkg = json.loads(
            (Path(result) / "deployment" / "cdk8s" / "package.json").read_text()
        )
        assert pkg["name"] == "kup-tfv-deployment"


def test_cdk8s_main_ts_image():
    """main.ts references the correct container image."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = generate_project(
            {"organization": "kup", "project_name": "tfv"},
            output_dir=tmpdir,
        )
        main_ts = (Path(result) / "deployment" / "cdk8s" / "main.ts").read_text()
        assert "ghcr.io/kup/kup-tfv" in main_ts


def test_cdk8s_main_ts_chart_class():
    """main.ts has chart class with capitalized project name."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = generate_project(
            {"organization": "kup", "project_name": "tfv"},
            output_dir=tmpdir,
        )
        main_ts = (Path(result) / "deployment" / "cdk8s" / "main.ts").read_text()
        assert "TfvChart" in main_ts
        assert "kup-tfv" in main_ts


def test_cdk8s_default_includes_all():
    """Default generation includes varnish, ingress, and cnpg files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = generate_project(
            {"organization": "testorg", "project_name": "testproject"},
            output_dir=tmpdir,
        )
        cdk8s = Path(result) / "deployment" / "cdk8s"
        main_ts = (cdk8s / "main.ts").read_text()
        assert "PloneHttpcache" in main_ts
        assert "PloneIngress" in main_ts
        assert "CloudNativePGCluster" in main_ts
        assert (cdk8s / "postgres.ts").exists()
        assert (cdk8s / "ingress.ts").exists()


def test_cdk8s_no_varnish():
    """Disabling varnish removes PloneHttpcache from main.ts."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = generate_project(
            {
                "organization": "testorg",
                "project_name": "testproject",
                "include_varnish": "no",
            },
            output_dir=tmpdir,
        )
        main_ts = (
            Path(result) / "deployment" / "cdk8s" / "main.ts"
        ).read_text()
        assert "PloneHttpcache" not in main_ts


def test_cdk8s_no_ingress():
    """Disabling ingress removes PloneIngress from main.ts."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = generate_project(
            {
                "organization": "testorg",
                "project_name": "testproject",
                "include_ingress": "no",
            },
            output_dir=tmpdir,
        )
        cdk8s = Path(result) / "deployment" / "cdk8s"
        main_ts = (cdk8s / "main.ts").read_text()
        assert "PloneIngress" not in main_ts
        # ingress.ts is removed by post_gen hook, but hook may not run
        # in this test context, so we only check main.ts content


def test_cdk8s_no_cnpg():
    """Disabling CNPG removes CloudNativePGCluster from main.ts."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = generate_project(
            {
                "organization": "testorg",
                "project_name": "testproject",
                "include_cnpg": "no",
            },
            output_dir=tmpdir,
        )
        cdk8s = Path(result) / "deployment" / "cdk8s"
        main_ts = (cdk8s / "main.ts").read_text()
        assert "CloudNativePGCluster" not in main_ts
        # Fallback env should be present
        assert "db-host" in main_ts


def test_cdk8s_env_example():
    """env.example has correct project defaults."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = generate_project(
            {"organization": "kup", "project_name": "tfv"},
            output_dir=tmpdir,
        )
        env = (
            Path(result) / "deployment" / "cdk8s" / ".env.example"
        ).read_text()
        assert "ghcr.io/kup/kup-tfv" in env
        assert "tfv.example.com" in env


def test_cdk8s_yaml_cnpg_import():
    """cdk8s.yaml includes CNPG CRD import when enabled."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = generate_project(
            {"organization": "testorg", "project_name": "testproject"},
            output_dir=tmpdir,
        )
        cdk8s_yaml = (
            Path(result) / "deployment" / "cdk8s" / "cdk8s.yaml"
        ).read_text()
        assert "cloudnative-pg" in cdk8s_yaml


def test_cdk8s_yaml_no_cnpg_import():
    """cdk8s.yaml excludes CNPG CRD import when disabled."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = generate_project(
            {
                "organization": "testorg",
                "project_name": "testproject",
                "include_cnpg": "no",
            },
            output_dir=tmpdir,
        )
        cdk8s_yaml = (
            Path(result) / "deployment" / "cdk8s" / "cdk8s.yaml"
        ).read_text()
        assert "cloudnative-pg" not in cdk8s_yaml


def test_dockerignore_excludes_cdk8s():
    """dockerignore excludes deployment/cdk8s/ from image build."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = generate_project(
            {"organization": "testorg", "project_name": "testproject"},
            output_dir=tmpdir,
        )
        dockerignore = (Path(result) / ".dockerignore").read_text()
        assert "deployment/cdk8s/" in dockerignore


def test_cdk8s_main_ts_has_plone_construct():
    """main.ts uses the Plone construct with start-backend/start-frontend args."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = generate_project(
            {"organization": "testorg", "project_name": "testproject"},
            output_dir=tmpdir,
        )
        main_ts = (
            Path(result) / "deployment" / "cdk8s" / "main.ts"
        ).read_text()
        assert "new Plone(" in main_ts
        assert "start-backend" in main_ts
        assert "start-frontend" in main_ts
