# Airsonic Playlist Sync - Copilot Agent Instructions

## Project Overview

**Airsonic Playlist Sync** is a Python-based Docker tool that automatically syncs music from an Airsonic/OpenSubsonic shared folder to a playlist, maintaining only the N most recent episodes. It extracts dates from filenames (YYYYMMDD format) for sorting.

- **Type**: Scheduled sync tool (Docker-containerized Python script)
- **Languages**: Python 3.11+
- **Runtime**: Docker (podman or docker, auto-detected in Makefile)
- **Key Dependencies**: `requests>=2.31.0` (see requirements.txt)
- **Configuration**: `config.json` (copy from `config.example.json`)

## Project Layout

```
/
├── docker/
│   └── Dockerfile              # Container build
├── docs/                       # Documentation
├── scripts/                    # Helper scripts
├── src/
│   ├── sync_playlist.py        # Main sync script
│   └── discover.py             # Discover folder/playlist IDs
├── systemd/                    # Systemd service files
├── logs/                       # Runtime logs (gitignored)
├── config.json                 # Local config (gitignored, copy from example)
├── config.example.json         # Config template
├── requirements.txt            # Python dependencies
└── Makefile                    # Build/run targets
```

## Build & Run Commands (Validated)

### Prerequisites
```bash
# ALWAYS copy config before first run
cp config.example.json config.json
# Edit config.json with your Airsonic server details
```

### Make Targets (use `make help` to list all)
```bash
make build       # Build container image (uses podman if available, else docker)
make run-dry     # Test run in dry-run mode (no actual changes)
make run         # Run sync once
make discover    # Find folder/playlist IDs from your Airsonic server
make up          # Start as a daemon
make down        # Stop daemon
make logs        # Show logs
make clean       # Remove container image
```

**Note**: The Makefile auto-detects `podman` or `docker`. Always prefer `make` targets over direct docker commands.

### Running Tests
```bash
# CI uses test.yml workflow
# Local: tests are run via pytest inside container
podman build -f docker/Dockerfile -t airsonic-playlist-sync:latest .
```

## CI/CD Workflows (`.github/workflows/`)

- **build-and-publish.yml**: Builds and publishes Docker image to GitHub Container Registry
- **test.yml**: Runs pytest test suite
- **cleanup.yml**: Cleans old artifacts

## Key Configuration (`config.json`)
- `server`: Airsonic server URL
- `username` / `password`: Credentials
- `folder_id`: Source folder to sync from (use `make discover` to find)
- `playlist_id`: Target playlist ID (use `make discover` to find)
- `max_songs`: Number of most recent songs to keep (default: 15)

## Common Pitfalls
- `config.json` is gitignored — always copy from `config.example.json` first
- DNS flags (`--dns=192.168.7.12`) are hardcoded in Makefile for local network resolution
- Logs directory is auto-created by `make run`

## Trust these instructions first. Only search if information here is incomplete.
