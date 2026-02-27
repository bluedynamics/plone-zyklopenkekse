#!/bin/bash
set -e

# ---------------------------------------------------------------------------
# Cyclop OCI Image Entrypoint
#
# Built-in commands: start-backend, start-frontend, export, import, pack
# Extensible: drop scripts into /backend/deployment/commands.d/<command>.sh
# ---------------------------------------------------------------------------

# Drop-in command extension
# Project-specific commands go in /backend/deployment/commands.d/<name>.sh
COMMAND_SCRIPT="/backend/deployment/commands.d/$1.sh"
if [[ -f "$COMMAND_SCRIPT" ]]; then
    echo "Running project command: $1"
    exec bash "$COMMAND_SCRIPT" "${@:2}"
fi

# Helper: generate Zope instance from environment variables
setup_zope() {
    python /backend/deployment/transform_from_environment.py \
        -o "$ZOPE_CONFIGURATION_FILE"
    cd /backend && make zope-instance
}

# Built-in commands
case "$1" in
    start-backend)
        echo "Setting up Zope instance from environment"
        setup_zope
        echo "Starting Plone backend"
        exec make zope-start
        ;;
    start-frontend)
        echo "Starting Volto frontend"
        cd /frontend && exec pnpm start:prod
        ;;
    export)
        setup_zope
        echo "Exporting ZODB to filestorage"
        exec zodbconvert --clear /backend/instance/etc/relstorage-export.conf
        ;;
    import)
        setup_zope
        echo "Importing filestorage to ZODB"
        exec zodbconvert --clear /backend/instance/etc/relstorage-import.conf
        ;;
    pack)
        setup_zope
        echo "Packing ZODB"
        exec zodbpack /backend/instance/etc/relstorage-pack.conf
        ;;
    *)
        exec "$@"
        ;;
esac
