# Airsonic Playlist Sync

[![Build and Publish](https://github.com/slmingol/airsonic-playlist-sync/actions/workflows/build-and-publish.yml/badge.svg)](https://github.com/slmingol/airsonic-playlist-sync/actions/workflows/build-and-publish.yml)
[![Test](https://github.com/slmingol/airsonic-playlist-sync/actions/workflows/test.yml/badge.svg)](https://github.com/slmingol/airsonic-playlist-sync/actions/workflows/test.yml)
[![Cleanup](https://github.com/slmingol/airsonic-playlist-sync/actions/workflows/cleanup.yml/badge.svg)](https://github.com/slmingol/airsonic-playlist-sync/actions/workflows/cleanup.yml)
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/slmingol/airsonic-playlist-sync?label=release)](https://github.com/slmingol/airsonic-playlist-sync/releases/latest)
[![GitHub last commit](https://img.shields.io/github/last-commit/slmingol/airsonic-playlist-sync)](https://github.com/slmingol/airsonic-playlist-sync/commits/main)
[![GitHub issues](https://img.shields.io/github/issues/slmingol/airsonic-playlist-sync)](https://github.com/slmingol/airsonic-playlist-sync/issues)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Platforms](https://img.shields.io/badge/platform-amd64%20%7C%20arm64-lightgrey)](https://github.com/slmingol/airsonic-playlist-sync/pkgs/container/airsonic-playlist-sync)
[![Container](https://img.shields.io/badge/ghcr.io-airsonic--playlist--sync-blue)](https://github.com/slmingol/airsonic-playlist-sync/pkgs/container/airsonic-playlist-sync)

Automatically sync music from an Airsonic/OpenSubsonic folder to a playlist, maintaining only the N most recent episodes.

## Features

- **Smart Sync**: Maintains exactly N most recent songs (configurable, default 25)
- **Date-Aware**: Extracts dates from filenames (YYYYMMDD format) for proper sorting
- **Auto-Add**: Automatically adds new songs from monitored folder
- **Auto-Remove**: Removes old songs beyond the limit to keep playlist fresh
- **Dry-Run Mode**: Preview changes before applying them
- **OpenSubsonic Compatible**: Works with Airsonic-Advanced and other compatible servers
- **Secure**: MD5 salted token authentication
- **Container Ready**: Docker/Podman support with multi-arch images (amd64/arm64)
- **Schedulable**: Run via cron, systemd timer, or Docker Compose scheduler

## Quick Start

### Using Makefile

```bash
make build              # Build container image
make discover           # Find folder/playlist IDs
make list               # List current playlist contents
make run-dry            # Preview changes (dry-run)
make run                # Apply sync
make run MAX_SONGS=10   # Sync with custom episode limit (default: 25)
```

### Using Docker/Podman

```bash
# Pull the image
docker pull ghcr.io/slmingol/airsonic-playlist-sync:latest

# Create config file
cp config.example.json config.json
# Edit config.json with your server URL, username, password, and IDs

# Discover folder and playlist IDs
docker run --rm \
  --entrypoint python3 \
  -v $(pwd)/config.json:/config/config.json \
  ghcr.io/slmingol/airsonic-playlist-sync:latest \
  /app/discover.py --config /config/config.json

# List current playlist contents
docker run --rm \
  --entrypoint python3 \
  -v $(pwd)/config.json:/config/config.json \
  ghcr.io/slmingol/airsonic-playlist-sync:latest \
  /app/discover.py --config /config/config.json --list

# Dry-run sync
docker run --rm \
  -v $(pwd)/config.json:/config/config.json \
  -v $(pwd)/logs:/app/logs \
  ghcr.io/slmingol/airsonic-playlist-sync:latest --dry-run

# Run actual sync
docker run --rm \
  -v $(pwd)/config.json:/config/config.json \
  -v $(pwd)/logs:/app/logs \
  ghcr.io/slmingol/airsonic-playlist-sync:latest

# Keep only 10 most recent episodes
docker run --rm \
  -v $(pwd)/config.json:/config/config.json \
  -v $(pwd)/logs:/app/logs \
  ghcr.io/slmingol/airsonic-playlist-sync:latest --max-songs 10
```

### Using Python

```bash
# Install dependencies
pip install -r requirements.txt

# Discover IDs
python src/discover.py --config config.json

# List current playlist
python src/discover.py --config config.json --list

# Run sync
python src/sync_playlist.py --dry-run
python src/sync_playlist.py
```

## Configuration

Create `config.json` from the example:

```bash
cp config.example.json config.json
```

```json
{
  "server_url": "https://your-airsonic-server.com",
  "username": "your_username",
  "password": "your_password",
  "api_version": "1.15.0",
  "client_name": "PlaylistSync",
  "source_directory_id": "12345",
  "target_playlist_id": "67890"
}
```

Run `make discover` to find your `source_directory_id` and `target_playlist_id`.

## Usage Options

### Command Line Arguments

```bash
# Keep only 10 most recent episodes
python src/sync_playlist.py --max-songs 10

# Dry run with custom limit
python src/sync_playlist.py --max-songs 25 --dry-run

# Use custom config file
python src/sync_playlist.py --config /path/to/config.json
```

### Automated Scheduling

**Cron:**
```bash
# Run every 6 hours
0 */6 * * * cd /path/to/airsonic-playlist-sync && python src/sync_playlist.py
```

**Docker Compose (scheduled):**
```bash
docker-compose -f docker/docker-compose.scheduled.yml up -d
```

**Systemd:**
```bash
# Copy service files
sudo cp systemd/airsonic-sync-docker.{service,timer} /etc/systemd/system/

# Enable and start
sudo systemctl enable --now airsonic-sync-docker.timer
```

## Documentation

- [Quickstart Guide](docs/QUICKSTART.md)
- [Docker Setup](docs/DOCKER.md)
- [Detailed README](docs/README.md)

## Development

```bash
# Clone repository
git clone https://github.com/slmingol/airsonic-playlist-sync.git
cd airsonic-playlist-sync

# Install dependencies
pip install -r requirements.txt

# Run linting
flake8 src/

# Build container locally
make build
```

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details

## Support

- [Report Issues](https://github.com/slmingol/airsonic-playlist-sync/issues)
- [Request Features](https://github.com/slmingol/airsonic-playlist-sync/issues)
- [View Documentation](docs/)
