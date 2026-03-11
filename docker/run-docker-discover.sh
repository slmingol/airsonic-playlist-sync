#!/bin/bash
# Helper script to run discovery in Docker/Podman

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

# Detect container runtime
if command -v podman &> /dev/null; then
    CONTAINER_CMD="podman"
elif command -v docker &> /dev/null; then
    CONTAINER_CMD="docker"
else
    echo "Error: Neither Docker nor Podman found!"
    echo "Please install Docker or Podman to use this script."
    exit 1
fi

echo "Using container runtime: $CONTAINER_CMD"
Container build failed!"
    exit 1
fi

# Run the discovery tool in container
echo "Running discovery in container..."
echo
$CONTAINER_CMD run --rm -it \
    -v "$SCRIPT_DIR/config.json:/config/config.json:ro
$CONTAINER_CMD build -t airsonic-playlist-sync:latest .

if [ $? -ne 0 ]; then
    echo "Error: Docker build failed!"
    exit 1
fi

# Run the discovery tool in container
echo "Running discovery in container..."
echo
docker run --rm -it \
    -v "$SCRIPT_DIR/config.json:/config/config.json:ro" \
    -e TZ="$(readlink /etc/localtime | sed 's#/var/db/timezone/zoneinfo/##')" \
    airsonic-playlist-sync:latest \
    python3 /app/discover.py --config /config/config.json
