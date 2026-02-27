# Zyklopenkekse Roadmap

## Vision

A cookieplone-based template that generates a Plone/Volto monorepo with:

- **mxmake Makefiles everywhere** — backend and frontend, both generated
- **One Dockerfile** for both frontend and backend (kup.tfv-style entrypoint pattern)
- **cdk8s-plone deployment** that ArgoCD can watch
- No Ansible/Swarm devops cruft

## Work Streams

### 1. Extend mxmake with Volto/frontend domains

New topic `frontend` (or extend existing `js`):

- `frontend.volto` — pnpm install, mrs-developer, dev server (`pnpm start`), production build (`pnpm build`), sentinel tracking
- `frontend.volto-qa` — eslint, prettier, stylelint (mirrors how `qa.ruff`/`qa.zpretty` work for backend)
- `frontend.volto-test` — jest unit tests, possibly acceptance test scaffolding
- `frontend.volto-i18n` — translation sync (`pnpm i18n`)
- Settings: volto version, node version, pnpm version, addon name, package manager choice

This is the **biggest piece of work** and lives in the mxmake repo.

### 2. Build the unified Dockerfile

Single multi-stage Dockerfile producing **one image** for all roles:

- `backend-build` stage: uv + Python, `make packages cookiecutter`
- `frontend-build` stage: Node + pnpm, mrs-developer, `pnpm build`
- `runtime` stage: debian:trixie-slim, copies venv + site + app + node
- Entrypoint dispatches: `start-backend`, `start-frontend`, `export`, `import`, `pack`
- **Extensible via drop-in scripts** in `deployment/commands.d/` for custom
  commands (e.g. background workers like pgcatalog Tika extraction)
- Same image used for all k8s Deployments, `args` selects the role
- Version sync guaranteed: one build, one tag, one rollback

### 3. Create the zyklopenkekse cookiecutter template

Based on cookieplone's sub-template composition pattern (or simplified variant).

`cookiecutter.json` — project name, slug, plone version, volto version, hostname, etc.

Generates:

- `backend/` — mxmake Makefile, mx.ini, instance.yaml, pyproject.toml, src/ skeleton
- `frontend/` — mxmake Makefile (new!), package.json, pnpm workspace, volto addon skeleton
- `deployment/` — cdk8s-plone TypeScript project (main.ts, package.json, cdk8s.yaml)
- Root `Makefile` — uses mxmake's `core.proxy` to delegate to backend/frontend/deployment
- `Dockerfile` — the unified build
- Minimal CI (GitLab or GitHub Actions): build images, cdk8s synth, commit manifests

### 4. Wire up cdk8s-plone deployment

Template generates a `deployment/` directory with:

- `main.ts` using `Plone` and optionally `PloneHttpcache` constructs
- Configurable via environment (image tags, replicas, domain, DB connection)
- `dist/` directory for synthesized manifests (ArgoCD target)
- Make target: `make deploy-synth` runs `cdk8s synth`

ArgoCD points at `deployment/dist/` in the repo.

## Phases

| Phase | What | Where |
|-------|------|-------|
| **A** | Design and implement mxmake Volto domains | mxmake repo | DONE |
| **B** | Design unified Dockerfile pattern | zyklopenkekse repo | DONE |
| **C** | Build cookiecutter template structure | zyklopenkekse repo | DONE |
| **D** | Wire in cdk8s-plone deployment template | zyklopenkekse repo | DONE |
| **E** | Root Makefile with proxy delegation | zyklopenkekse repo | DONE |
| **F** | CI pipeline template | zyklopenkekse repo | DONE |

Phase A is the prerequisite — without mxmake frontend domains, the template can't generate frontend Makefiles. Everything else can be somewhat parallel once A is done.
