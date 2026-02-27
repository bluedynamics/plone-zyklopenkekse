# {{ cookiecutter.title }}

{% if cookiecutter.include_frontend == "yes" %}
Plone {{ cookiecutter.plone_version }} / Volto {{ cookiecutter.volto_version }} monorepo for **{{ cookiecutter.organization }}**.
{% else %}
Plone {{ cookiecutter.plone_version }} (ClassicUI) project for **{{ cookiecutter.organization }}**.
{% endif %}

## Structure

```
{{ cookiecutter.__target }}/
  backend/       Plone backend (Python, mxmake)
{% if cookiecutter.include_frontend == "yes" %}
  frontend/      Volto frontend (TypeScript, pnpm, mxmake)
{% endif %}
  deployment/    Container entrypoint + cdk8s Kubernetes manifests
{% if cookiecutter.include_frontend == "yes" %}
  Dockerfile     Unified multi-stage image (backend + frontend)
  Makefile       Root orchestration (delegates to backend/frontend)
{% else %}
  Dockerfile     Multi-stage image (backend)
  Makefile       Root orchestration (delegates to backend)
{% endif %}
```

## Quick Start

```bash
{% if cookiecutter.include_frontend == "yes" %}
make install          # install backend + frontend
make backend-start    # start Plone on http://localhost:8080
make frontend-start   # start Volto on http://localhost:3000
{% else %}
make install          # install backend
make backend-start    # start Plone on http://localhost:8080
{% endif %}
```

## Common Tasks

| Command | Description |
|---------|-------------|
{% if cookiecutter.include_frontend == "yes" %}
| `make install` | Install backend and frontend |
{% else %}
| `make install` | Install backend |
{% endif %}
| `make check` | Run all code checks |
| `make format` | Format all code |
| `make test` | Run all tests |
{% if cookiecutter.include_frontend == "yes" %}
| `make i18n` | Sync frontend translations |
{% endif %}
| `make build-image` | Build Docker image |
| `make clean` | Clean all installations |
| `make help` | Show all available targets |

{% if cookiecutter.include_frontend == "yes" %}
See the `backend/`, `frontend/`, and `deployment/` directories for component-specific documentation.
{% else %}
See the `backend/` and `deployment/` directories for component-specific documentation.
{% endif %}

## Docker Image

{% if cookiecutter.include_frontend == "yes" %}
A single image serves both backend and frontend, selected via entrypoint argument:

```bash
make build-image
docker run {{ cookiecutter.__container_registry }}/{{ cookiecutter.__target }}:latest start-backend
docker run {{ cookiecutter.__container_registry }}/{{ cookiecutter.__target }}:latest start-frontend
```
{% else %}
```bash
make build-image
docker run {{ cookiecutter.__container_registry }}/{{ cookiecutter.__target }}:latest start-backend
```
{% endif %}

## Technology Stack

- **Backend**: Plone {{ cookiecutter.plone_version }}, Python {{ cookiecutter.python_version }}
{% if cookiecutter.include_frontend == "yes" %}
- **Frontend**: Volto {{ cookiecutter.volto_version }}, Node.js {{ cookiecutter.node_version }}, pnpm {{ cookiecutter.pnpm_version }}
{% endif %}
- **Deployment**: cdk8s-plone (Kubernetes via ArgoCD)
{% if cookiecutter.include_frontend == "yes" %}
- **Build**: mxmake (Makefile generation for both backend and frontend)
{% else %}
- **Build**: mxmake (Makefile generation for backend)
{% endif %}
