# Deployment

Container runtime and Kubernetes deployment for {{ cookiecutter.title }}.

## Container Image

The project uses a unified multi-stage Docker image (see `../Dockerfile`).
{% if cookiecutter.include_frontend == "yes" %}
A single image serves all roles, selected via the entrypoint argument:
{% else %}
The image serves backend roles, selected via the entrypoint argument:
{% endif %}

| Command | Port | Description |
|---------|------|-------------|
| `start-backend` | 8080 | Plone/Zope application server |
{% if cookiecutter.include_frontend == "yes" %}
| `start-frontend` | 3000 | Volto Node.js server |
{% endif %}
| `export` | - | ZODB export |
| `import` | - | ZODB import |
| `pack` | - | ZODB pack (garbage collection) |

Build the image:

```bash
make build-image                          # from project root
docker build . -t my-image:latest         # or directly
```

## Entrypoint

`entrypoint.sh` dispatches the container command. It supports extension via
drop-in scripts in `commands.d/`:

```
deployment/
  entrypoint.sh       Main entrypoint (dispatches commands)
  commands.d/          Drop-in command scripts
    *.sh               Custom commands (e.g. worker.sh, migrate.sh)
```

To add a custom command (e.g. a background worker):

1. Create `commands.d/my-worker.sh`
2. Run: `docker run <image> my-worker`

## Kubernetes (cdk8s)

The `cdk8s/` directory contains a [cdk8s-plone](https://github.com/bluedynamics/cdk8s-plone)
TypeScript project that synthesizes Kubernetes manifests.

### Setup

```bash
cd cdk8s
npm install
npx cdk8s import    # generate CRD type bindings
```

### Configuration

Copy `.env.example` to `.env` and adjust values:

```bash
cp .env.example .env
```

Key variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `IMAGE` | `{{ cookiecutter.__container_registry }}/{{ cookiecutter.__target }}` | Container image |
| `IMAGE_TAG` | `latest` | Image tag |
| `DOMAIN` | `{{ cookiecutter.project_name }}.example.com` | Public domain |
| `BACKEND_REPLICAS` | `2` | Backend pod count |
{% if cookiecutter.include_frontend == "yes" -%}
| `FRONTEND_REPLICAS` | `2` | Frontend pod count |
{% endif -%}
{% if cookiecutter.include_cnpg == "yes" -%}
| `PG_INSTANCES` | `2` | PostgreSQL instances (CloudNativePG) |
| `PG_STORAGE` | `20Gi` | PostgreSQL storage size |
{% endif -%}

### Synthesize Manifests

```bash
npx cdk8s synth     # outputs to dist/
```

The `dist/` directory contains plain Kubernetes YAML manifests ready for
ArgoCD or `kubectl apply`.

### Components

{% if cookiecutter.include_varnish == "yes" -%}
- **Varnish** (HTTP cache) - routes public traffic through cache layer
{% endif -%}
{% if cookiecutter.include_ingress == "yes" -%}
{% if cookiecutter.include_frontend == "yes" -%}
- **Ingress** - TLS termination via cert-manager, routes `++api++` to backend
{% else -%}
- **Ingress** - TLS termination via cert-manager, routes traffic to backend
{% endif -%}
{% endif -%}
{% if cookiecutter.include_cnpg == "yes" -%}
- **CloudNativePG** - PostgreSQL operator for automated HA databases
{% endif -%}

### ArgoCD Integration

Point ArgoCD at the `deployment/cdk8s/dist/` directory in your repository.
CI synthesizes manifests on every push to main.
