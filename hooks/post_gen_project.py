"""Post-generation hook: generate Makefiles via mxmake init."""
import os
import shutil
import subprocess


def run_mxmake_init(directory):
    """Run mxmake init with preseed in the given directory."""
    preseed = os.path.join(directory, "mxmake-preseed.yaml")
    if not os.path.exists(preseed):
        print(f"  Skipping {directory}: no mxmake-preseed.yaml found")
        return

    # Try mxmake directly, fall back to uvx
    mxmake = shutil.which("mxmake")
    if mxmake:
        cmd = [mxmake, "init", "--preseed", "mxmake-preseed.yaml"]
    else:
        uvx = shutil.which("uvx")
        if uvx:
            cmd = [uvx, "mxmake", "init", "--preseed", "mxmake-preseed.yaml"]
        else:
            print(f"  WARNING: neither mxmake nor uvx found, skipping {directory}")
            print("  Install mxmake and run: cd {directory} && mxmake init --preseed mxmake-preseed.yaml")
            return

    print(f"  Generating Makefile in {directory}...")
    result = subprocess.run(cmd, cwd=directory, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  WARNING: Makefile generation failed in {directory}:")
        print(f"  {result.stderr.strip()}")
        print(f"  You can generate it manually: cd {directory} && mxmake init --preseed mxmake-preseed.yaml")
        return
    print(f"  Makefile generated in {directory}")


def main():
    project_dir = os.getcwd()
    print("Post-generation: generating Makefiles with mxmake...")

    # Generate backend Makefile
    run_mxmake_init(os.path.join(project_dir, "backend"))

    # Generate frontend Makefile or remove frontend directory
    frontend_dir = os.path.join(project_dir, "frontend")
    if "{{ cookiecutter.include_frontend }}" == "yes":
        run_mxmake_init(frontend_dir)
    else:
        if os.path.isdir(frontend_dir):
            shutil.rmtree(frontend_dir)
            print("  Removed frontend/ (ClassicUI mode)")

    # Make entrypoint executable
    entrypoint = os.path.join(project_dir, "deployment", "entrypoint.sh")
    if os.path.exists(entrypoint):
        os.chmod(entrypoint, 0o755)

    # Remove conditional cdk8s files based on toggles
    cdk8s_dir = os.path.join(project_dir, "deployment", "cdk8s")
    if "{{ cookiecutter.include_cnpg }}" != "yes":
        postgres_ts = os.path.join(cdk8s_dir, "postgres.ts")
        if os.path.exists(postgres_ts):
            os.remove(postgres_ts)
            print("  Removed postgres.ts (CloudNativePG disabled)")

    if "{{ cookiecutter.include_ingress }}" != "yes":
        ingress_ts = os.path.join(cdk8s_dir, "ingress.ts")
        if os.path.exists(ingress_ts):
            os.remove(ingress_ts)
            print("  Removed ingress.ts (Ingress disabled)")

    # Remove unused CI files based on platform choice
    ci_platform = "{{ cookiecutter.ci_platform }}"
    if ci_platform != "github":
        github_dir = os.path.join(project_dir, ".github")
        if os.path.isdir(github_dir):
            shutil.rmtree(github_dir)
            print("  Removed .github/ (using GitLab CI)")
    if ci_platform != "gitlab":
        gitlab_ci = os.path.join(project_dir, ".gitlab-ci.yml")
        if os.path.exists(gitlab_ci):
            os.remove(gitlab_ci)
            print("  Removed .gitlab-ci.yml (using GitHub Actions)")

    # Try to run npm install and cdk8s import in deployment/cdk8s
    if os.path.isdir(cdk8s_dir):
        npm = shutil.which("npm")
        if npm:
            print("  Installing cdk8s dependencies...")
            result = subprocess.run(
                [npm, "install"], cwd=cdk8s_dir, capture_output=True, text=True
            )
            if result.returncode == 0:
                print("  Running cdk8s import...")
                npx = shutil.which("npx")
                if npx:
                    result = subprocess.run(
                        [npx, "cdk8s", "import"],
                        cwd=cdk8s_dir,
                        capture_output=True,
                        text=True,
                    )
                    if result.returncode != 0:
                        print(f"  WARNING: cdk8s import failed: {result.stderr.strip()}")
                        print("  Run manually: cd deployment/cdk8s && npx cdk8s import")
            else:
                print(f"  WARNING: npm install failed: {result.stderr.strip()}")
                print("  Run manually: cd deployment/cdk8s && npm install && npx cdk8s import")
        else:
            print("  WARNING: npm not found, skipping cdk8s setup")
            print("  Run manually: cd deployment/cdk8s && npm install && npx cdk8s import")

    print("Done! Your project is ready.")
    print(f"  cd {{ cookiecutter.__target }}")
    print("  cd backend && make install")
    if "{{ cookiecutter.include_frontend }}" == "yes":
        print("  cd ../frontend && make install")


if __name__ == "__main__":
    main()
