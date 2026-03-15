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

# Check if config.json exists
if [ ! -f "config.json" ]; then
    echo "Error: config.json not found!"
    echo "Please create config.json with your Airsonic credentials."
    exit 1
fi

# Build the container
echo "Building container image..."
$CONTAINER_CMD build -t airsonic-playlist-sync:latest -f docker/Dockerfile .

if [ $? -ne 0 ]; then
    echo "Error: Container build failed!"
    exit 1
fi

# Run the discovery tool in container
echo "Running discovery in container..."
echo
$CONTAINER_CMD run --rm -it \
    -v "$PROJECT_DIR/config.json:/config/config.json:ro" \
    -e TZ="${TZ:-UTC}" \
    airsonic-playlist-sync:latest \
    python3 /app/discover.py --config /config/config.json
