# {{ cookiecutter.title }}

Plone {{ cookiecutter.plone_version }} / Volto {{ cookiecutter.volto_version }} monorepo for **{{ cookiecutter.organization }}**.

## Structure

```
{{ cookiecutter.__target }}/
  backend/       Plone backend (Python, mxmake)
  frontend/      Volto frontend (TypeScript, pnpm, mxmake)
  deployment/    Container entrypoint + cdk8s Kubernetes manifests
  Dockerfile     Unified multi-stage image (backend + frontend)
  Makefile       Root orchestration (delegates to backend/frontend)
```

## Quick Start

```bash
make install          # install backend + frontend
make backend-start    # start Plone on http://localhost:8080
make frontend-start   # start Volto on http://localhost:3000
```

## Common Tasks

| Command | Description |
|---------|-------------|
| `make install` | Install backend and frontend |
| `make check` | Run all code checks |
| `make format` | Format all code |
| `make test` | Run all tests |
| `make i18n` | Sync frontend translations |
| `make build-image` | Build Docker image |
| `make clean` | Clean all installations |
| `make help` | Show all available targets |

See the `backend/`, `frontend/`, and `deployment/` directories for component-specific documentation.

## Docker Image

A single image serves both backend and frontend, selected via entrypoint argument:

```bash
make build-image
docker run {{ cookiecutter.__container_registry }}/{{ cookiecutter.__target }}:latest start-backend
docker run {{ cookiecutter.__container_registry }}/{{ cookiecutter.__target }}:latest start-frontend
```

## Technology Stack

- **Backend**: Plone {{ cookiecutter.plone_version }}, Python {{ cookiecutter.python_version }}
- **Frontend**: Volto {{ cookiecutter.volto_version }}, Node.js {{ cookiecutter.node_version }}, pnpm {{ cookiecutter.pnpm_version }}
- **Deployment**: cdk8s-plone (Kubernetes via ArgoCD)
- **Build**: mxmake (Makefile generation for both backend and frontend)
