#!/bin/bash
# Helper script to run the sync in Docker/Podman

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

# Create logs directory if it doesn't exist
mkdir -p logs
Container build failed!"
    exit 1
fi

# Run the container
echo "Running sync in container..."
$CONTAINER_CMD run --rm \
    -v "$SCRIPT_DIR/config.json:/config/config.json:ro" \
    -v "$SCRIPT_DIR/logs:/app/logs
$CONTAINER_CMD build -t airsonic-playlist-sync:latest .

if [ $? -ne 0 ]; then
    echo "Error: Docker build failed!"
    exit 1
fi

# Run the container
echo "Running sync in container..."
docker run --rm \
    -v "$SCRIPT_DIR/config.json:/config/config.json:ro" \
    -v "$SCRIPT_DIR/logs:/app/logs" \
    -e TZ="$(readlink /etc/localtime | sed 's#/var/db/timezone/zoneinfo/##')" \
    airsonic-playlist-sync:latest \
    python3 /app/sync_playlist.py --config /config/config.json $DRY_RUN

echo
echo "Done! Check logs/ directory for output."
