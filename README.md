# Zyklopenkekse

*German for "cyclops cookies" -- one-eyed biscuits with a single jam dot in the center, a beloved Austrian/German holiday treat.*
(also available with three dots)

**One Mono-Repo, all-in-one OCI-image.**
Very opinionated, built for cloud native deployments.

A [cookiecutter](https://cookiecutter.readthedocs.io/) template that generates production-ready **Plone 6** projects -- with **Volto** frontend or **ClassicUI**-only.

## Quick start

```bash
# Interactive mode (TUI)
uvx plone-zyklopenkekse

# Non-interactive
uvx cookiecutter gh:bluedynamics/plone-zyklopenkekse
```

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

## Documentation

Rendered documentation: **https://bluedynamics.github.io/plone-zyklopenkekse/**

- [Quickstart tutorial](https://bluedynamics.github.io/plone-zyklopenkekse/tutorials/quickstart.html) -- generate your first project
- [Template options](https://bluedynamics.github.io/plone-zyklopenkekse/how-to/choose-options.html) -- all toggles and settings explained
- [Architecture](https://bluedynamics.github.io/plone-zyklopenkekse/explanation/architecture.html) -- how it all fits together

## Requirements

- Python >= 3.12
- [uv](https://docs.astral.sh/uv/)

## Development

```bash
git clone git@github.com:bluedynamics/plone-zyklopenkekse.git
cd plone-zyklopenkekse
uv run --extra test pytest tests/ -x -q
```

## Source Code and Contributions

The source code is managed in a Git repository, with its main branches hosted on GitHub.
Issues can be reported there too.

We'd be happy to see many forks and pull requests to make this template even better.
We welcome AI-assisted contributions, but expect every contributor to fully understand and be able to explain the code they submit.
Please don't send bulk auto-generated pull requests.

Maintainers are Jens Klein and the BlueDynamics Alliance developer team.
We appreciate any contribution and if a release on PyPI is needed, please just contact one of us.
We also offer commercial support if any training, coaching, integration or adaptations are needed.

## License

BSD-2-Clause
