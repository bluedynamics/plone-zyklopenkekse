# Zyklopenkekse

*German for "cyclops cookies" — one-eyed biscuits with a single jam dot in the center, a beloved Austrian/German holiday treat.*
(also available with three dots)

A [cookiecutter](https://cookiecutter.readthedocs.io/) template that generates production-ready **Plone 6** projects — with **Volto** frontend or **ClassicUI**-only.

## What you get

```
<org>-<project>/
  backend/          Plone backend (mxmake, uv, ruff, zpretty)
  frontend/         Volto frontend (pnpm, mrs-developer, custom addon)  [optional]
  deployment/       cdk8s-plone Kubernetes manifests (optional Varnish, Ingress, CNPG)
  Dockerfile        Unified multi-stage image (backend + optional frontend)
  Makefile          Orchestration across backend/frontend
  .github/          GitHub Actions CI  \
  .gitlab-ci.yml    GitLab CI           } one of these, your choice
```

## Features

- **Volto or ClassicUI** — toggle `include_frontend` to generate with or without a Volto frontend
- **mxmake-driven builds** in both backend and frontend
- **Single Docker image** for all roles (backend, frontend, worker) via entrypoint dispatch
- **Multi-arch images** (amd64 + arm64)
- **cdk8s-plone** deployment with optional Varnish HTTP cache, Ingress, and CloudNativePG
- **CI pipelines** for GitHub Actions or GitLab CI (selectable)
- **Textual TUI** for interactive project creation with live version fetching

## Requirements

- Python >= 3.12
- [uv](https://docs.astral.sh/uv/)

## Quick start

```bash
# Interactive mode (TUI)
uvx plone-zyklopenkekse

# Non-interactive
uvx cookiecutter gh:bluedynamics/plone-zyklopenkekse
```

## Development

```bash
git clone git@github.com:bluedynamics/plone-zyklopenkekse.git
cd plone-zyklopenkekse
uv run --extra test pytest tests/ -x -q
```

## License

BSD-2-Clause
