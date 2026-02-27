# syntax=docker/dockerfile:1
#
# {{ cookiecutter.title }}: Unified Plone/Volto OCI Image
#
# Produces a single image that runs as backend, frontend, or worker
# depending on the command argument:
#
#   docker run <image> start-backend     # Plone on :8080
#   docker run <image> start-frontend    # Volto on :3000
#   docker run <image> export            # ZODB export
#   docker run <image> import            # ZODB import
#   docker run <image> pack              # ZODB pack
#
# Extensible via drop-in scripts in deployment/commands.d/

ARG PYTHON_VERSION={{ cookiecutter.python_version }}
ARG NODE_VERSION={{ cookiecutter.node_version }}
ARG PNPM_VERSION={{ cookiecutter.pnpm_version }}
ARG COOKIECUTTER_ZOPE_INSTANCE_VERSION=2.2.1

# =============================================================================
# Stage 1: Backend Build
# =============================================================================
FROM ghcr.io/astral-sh/uv:python${PYTHON_VERSION}-trixie-slim AS backend-build

ENV PYTHONDONTWRITEBYTECODE=1
ENV VENV_CREATE=false
ENV VENV_FOLDER=/venv
ENV VIRTUAL_ENV=/venv
ENV MXENV_UV_GLOBAL=true

RUN \
    apt-get update && \
    apt-get -y upgrade && \
    apt-get install -y --no-install-recommends \
        busybox \
        ca-certificates \
        git \
        libmagic1 \
        libpq-dev \
        make \
        wget && \
    busybox --install -s && \
    useradd --system -m -d /home/plone -U -u 500 plone && \
    uv venv /venv && \
    chown -R plone:plone /venv && \
    apt-get -y clean && \
    rm -rf /var/lib/apt/lists/*

USER plone
COPY --chown=plone:plone ./backend /backend
WORKDIR /backend

RUN \
    sed -i 's/\[test\]/\[production\]/g' /backend/requirements.txt && \
    export PATH=/venv/bin:$PATH && \
    make packages cookiecutter && \
    find /venv \( -type f -a -name '*.pyc' -o -name '*.pyo' \) -exec rm -rf '{}' + && \
    uv cache clean

# =============================================================================
# Stage 2: Frontend Build
# =============================================================================
FROM node:${NODE_VERSION}-slim AS frontend-build

RUN \
    apt-get update && \
    apt-get -y upgrade && \
    apt-get install -y --no-install-recommends \
        busybox \
        ca-certificates \
        git \
        make \
        wget && \
    busybox --install -s && \
    useradd --system -m -d /home/plone -U -u 500 plone && \
    npm i -g corepack@latest && \
    corepack enable && \
    apt-get -y clean && \
    rm -rf /var/lib/apt/lists/*

USER plone
COPY --chown=plone:plone ./frontend /frontend
WORKDIR /frontend

ARG PNPM_VERSION
RUN --mount=type=cache,id=pnpm,target=/frontend/.pnpm-store,uid=500 \
    corepack use pnpm@${PNPM_VERSION} && \
    pnpm dlx mrs-developer missdev --no-config --fetch-https && \
    pnpm install && \
    pnpm build:deps && \
    pnpm build && \
    CI=1 pnpm install --prod && \
    rm -rf core/.git .cache

# =============================================================================
# Stage 3: Runtime (final image)
# =============================================================================
FROM debian:trixie-slim AS runtime

ARG NODE_VERSION
ARG COOKIECUTTER_ZOPE_INSTANCE_VERSION

LABEL org.opencontainers.image.description="{{ cookiecutter.title }}: Unified Plone/Volto image"

# Runtime-only system dependencies
RUN \
    apt-get update && \
    apt-get -y upgrade && \
    apt-get install -y --no-install-recommends \
        busybox \
        ca-certificates \
        libmagic1 \
        libpq5 \
        make \
        wget && \
    busybox --install -s && \
    useradd --system -m -d /home/plone -U -u 500 plone && \
    mkdir -p /instance && \
    chown plone:plone /instance && \
    apt-get -y clean && \
    rm -rf /var/lib/apt/lists/*

# Node.js runtime (just the binaries, no build tools)
COPY --from=frontend-build /usr/local/bin/node /usr/local/bin/node
COPY --from=frontend-build /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN \
    ln -sf /usr/local/lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm && \
    npm i -g corepack@latest && \
    corepack enable

# Python venv from backend build
COPY --from=backend-build --chown=plone:plone /venv /venv

# Backend application
COPY --from=backend-build --chown=plone:plone /backend /backend

# Frontend application
COPY --from=frontend-build --chown=plone:plone /frontend /frontend

# Deployment scripts (cross-cutting, separate from backend/frontend)
COPY --chown=plone:plone ./deployment /deployment

# Download cookiecutter-zope-instance template for runtime config generation
RUN \
    wget -q -O /deployment/cookiecutter-zope-instance.zip \
        "https://github.com/plone/cookiecutter-zope-instance/archive/refs/tags/${COOKIECUTTER_ZOPE_INSTANCE_VERSION}.zip" && \
    wget -q -O /deployment/transform_from_environment.py \
        "https://raw.githubusercontent.com/plone/cookiecutter-zope-instance/${COOKIECUTTER_ZOPE_INSTANCE_VERSION}/helpers/transform_from_environment.py" && \
    chmod u+x /deployment/transform_from_environment.py && \
    chown -R plone:plone /deployment

# Environment
ENV PYTHONDONTWRITEBYTECODE=1
ENV VIRTUAL_ENV=/venv
ENV PATH="/venv/bin:$PATH"
ENV VENV_CREATE=false
ENV VENV_FOLDER=/venv
ENV MXENV_UV_GLOBAL=true

# Zope configuration (overridable at runtime)
ENV ZOPE_TEMPLATE=/deployment/cookiecutter-zope-instance.zip
ENV ZOPE_CONFIGURATION_FILE=/deployment/instance-from-environment.yaml
ENV ZOPE_TEMPLATE_CHECKOUT=
ENV ZOPE_BASE_FOLDER=/
ENV INSTANCE_target=/instance
ENV INSTANCE_debug_mode=false

USER plone
WORKDIR /backend

EXPOSE 8080 3000

HEALTHCHECK --interval=10s --timeout=5s --start-period=60s CMD exit 0

ENTRYPOINT ["/deployment/entrypoint.sh"]
