# Airsonic Playlist Sync

Automatically sync new music from an Airsonic folder to a playlist.

## Features

- 🎵 Automatically detect new songs in a folder/directory
- 📝 Add new songs to a playlist without duplicates
- 🔄 Can be run manually or scheduled with cron/systemd
- 🌐 Works with Airsonic-Advanced and other OpenSubsonic-compatible servers
- 🔐 Secure authentication using token-based auth (MD5 salt+password)

## Setup

You can run this tool either **natively with Python** or **in a Docker container**.

### Option A: Native Python Setup

#### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Or install the single dependency directly:
```#bash
pip install requests
```

### 2. Create Configuration File

Copy the example configuration:
```bash
cp config.example.json config.json
```

Edit `config.json` with your credentials:
```json
{
  "server_url": "https://airsonic-advanced.lamolabs.org",
  "username": "your_username",
  "password": "your_password",
  "api_version": "1.16.1",
  "client_name": "PlaylistSync"
}
```

#### 3. Discover Folder and Playlist IDs

Run the discovery script to find the IDs you need:
```bash
python3 discover.py
```

This will show you all available:
- Shares (including the folder and playlist from your shared links)
- Playlists
- Music folders

#### 4. Add IDs to Configuration

Update your `config.json` with the discovered IDs:
```json
{
  "server_url": "https://airsonic-advanced.lamolabs.org",
  "username": "your_username",
  "password": "your_password",
  "api_version": "1.16.1",
  "client_name": "PlaylistSync",
  "source_directory_id": "12345",
  "target_playlist_id": "67890"
}
```

Alternatively, you can use share IDs if you prefer:
```json
{
  "source_share_id": "ohBqV",
  "target_playlist_share_id": "OSWJN"
}
```

### Option B: Docker/Container Setup

#### 1. Prerequisites

- Docker installed on your system
- Docker Compose (optional, for scheduled runs)

#### 2. Create Configuration File

```# Run Once (Add Songs)

```bash
python3 sync_playlist.py
```

##### 3. Discover Folder and Playlist IDs

Use the discovery tool in a container:
```bash
# Using the helper script
./run-docker-discover.sh

# Or using make (auto-detects docker/podman)
make discover

# Or using docker directly
docker build -t airsonic-playlist-sync:latest .
docker run --rm -v "$(pwd)/config.json:/config/config.json:ro" \
  airsonic-playlist-sync:latest python3 /app/discover.py --config /config/config.json

# Or using podman
podman build -t airsonic-playlist-sync:latest .
podman run --rm -v "$(pwd)/config.json:/config/config.json:ro" \
  airsonic-playlist-sync:latest python3 /app/discover.py --config /config/config.json
```

#### 4. Add IDs to Configuration
#
Same as Option A - add `source_directory_id` and `target_playlist_id` to config.json.

---

## Usage

### Native Python

#### Run Once (Test Mode)

Run with `--dry-run` to see what would be added without making changes:
```bash
python3 sync_playlist.py --dry-run
```

### Run Once (Add Songs)

```bash
python3 sync_playlist.py
```

### Schedule with Cron

To run automatically every hour, add to your crontab:
```bash
crontab -e
```

Add this line:
```
0 * * * * cd /path/to/airsonic-playlist-sync && /usr/bin/python3 sync_playlist.py >> sync.log 2>&1
```
# Docker/Container

#### Run Once (Test Mode)

```bash
# Using the helper script
./run-docker.sh --dry-run

# Or using make (auto-detects docker/podman)
make run-dry

# Or using docker directly
docker build -t airsonic-playlist-sync:latest .
docker run --rm \
  -v "$(pwd)/config.json:/config/config.json:ro" \
  -v "$(pwd)/logs:/app/logs" \
  airsonic-playlist-sync:latest --dry-run

# Or using podman
podman build -t airsonic-playlist-sync:latest .
podman run --rm \
  -v "$(pwd)/config.json:/config/config.json:ro" \
  -v "$(pwd)/logs:/app/logs" \
  airsonic-playlist-sync:latest --dry-run
```

#### Run Once (Add Songs)

```bash
# Using the helper script
./run-docker.sh

# Or using make
make run

# Or using docker-compose
docker-compose up
```

#### Run on a Schedule (Background Container)
Docker Commands Quick Reference

| Command | Description |
|---------|-------------|
| `make help` | Show all available make commands |
| `make build` | Build the Docker image |
| `make run` | Run sync once in container |
| `make run-dry` | Run in dry-run mode |
| `make discover` | Run discovery tool |
| `make up` | Start scheduled sync (background) |
| `make down` | Stop scheduled sync |
| `make logs` | View container logs |
| `make clean` | Remove images and containers |

## Environment Variables (Docker)

When running in Docker, you can set these environment variables:

- `TZ` - Timezone (default: UTC, example: America/New_York)
- `SYNC_INTERVAL` - Seconds between syncs for scheduled mode (default: 3600)

## Security Notes

- Store `config.json` securely - it contains your password
- The config is mounted read-only in containers (`:ro`)
- Authentication uses salted MD5 tokens (not plain text passwords in URLs)
- Container runs as non-root user (UID 1000)
- Consider using Docker secrets for production deployments

## Files

- `sync_playlist.py` - Main sync script
- `discover.py` - Discovery tool for IDs
- `config.json` - Your credentials and settings
- `Dockerfile` - Container image definition
- `docker-compose.yml` - Run once configuration
- `docker-compose.scheduled.yml` - Scheduled sync configuration
- `Makefile` - Convenient make commands
- `run-docker.sh` - Helper script for Docker runs
- `run-docker-discover.sh` - Helper script for discovery
- `setup.sh` - Quick setup for native Python
- `setup-cron.sh` - Cron setup helper

# Or using docker-compose directly
docker-compose -f docker-compose.scheduled.yml up -d
```

Configuration:
- Edit `docker-compose.scheduled.yml` to change `SYNC_INTERVAL` (in seconds)
- Default: 3600 seconds (1 hour)
- Example: 900 for 15 minutes, 21600 for 6 hours

View logs:
```bash
make logs
# or
docker-compose -f docker-compose.scheduled.yml logs -f
```

Stop the scheduled container:
```bash
make down
# or
docker-compose -f docker-compose.scheduled.yml down
```

#### Using with Podman

Podman is Docker-compatible:
```bash
# Replace 'docker' with 'podman'
podman build -t airsonic-playlist-sync:latest .
podman run --rm \
  -v "$(pwd)/config.json:/config/config.json:ro" \
  -v "$(pwd)/logs:/app/logs" \
  airsonic-playlist-sync:latest

# Or use podman-compose instead of docker-compose
```

#### Schedule with Cron (Docker)

Add to crontab to run the containerized version:
```bash
0 * * * * cd /path/to/airsonic-playlist-sync && /path/to/docker run --rm -v "$(pwd)/config.json:/config/config.json:ro" airsonic-playlist-sync:latest >> logs/sync.log 2>&1
```

Or use the helper script:
```bash
0 * * * * cd /path/to/airsonic-playlist-sync && ./run-docker.sh >> logs/sync.log 2>&1
```

##
Or every 15 minutes:
```
*/15 * * * * cd /path/to/airsonic-playlist-sync && /usr/bin/python3 sync_playlist.py >> sync.log 2>&1
```

### Schedule with systemd (Linux)

Create a service file at `~/.config/systemd/user/airsonic-sync.service`:
```ini
[Unit]
Description=Airsonic Playlist Sync
After=network.target

[Service]
Type=oneshot
WorkingDirectory=/path/to/airsonic-playlist-sync
ExecStart=/usr/bin/python3 /path/to/airsonic-playlist-sync/sync_playlist.py
```

Create a timer file at `~/.config/systemd/user/airsonic-sync.timer`:
```ini
[Unit]
Description=Run Airsonic Playlist Sync hourly

[Timer]
OnBootSec=5min
OnUnitActiveSec=1h

[Install]
WantedBy=timers.target
```

Enable and start:
```bash
systemctl --user enable airsonic-sync.timer
systemctl --user start airsonic-sync.timer
```

## How It Works

1. **Authentication**: Uses secure token-based authentication (MD5 hash of password + random salt)
2. **Fetch Source Songs**: Recursively gets all songs from the source directory
3. **Fetch Playlist Songs**: Gets all songs currently in the playlist
4. **Compare**: Identifies songs in the source that aren't yet in the playlist
5. **Update**: Adds new songs to the playlist using the `updatePlaylist` API

## API Endpoints Used

- `ping` - Test connection
- `getShares` - Find shared folders/playlists
- `getPlaylists` - List all playlists
- `getMusicDirectory` - Get songs from a folder
- `getPlaylist` - Get playlist contents
- `updatePlaylist` - Add songs to playlist

## Troubleshooting

### Authentication Failed
- Verify your username and password are correct
- Make sure your account has API access enabled
- Check that the server URL is correct (no trailing slash)

### Can't Find Folder/Playlist IDs
- Run `python3 discover.py` to see all available IDs
- Make sure you're logged in as the user who owns the shares/playlists
- Check that the shares haven't expired

### No New Songs Added
- Verify the source directory contains songs
- Check that the songs aren't already in the playlist
- Run with `--dry-run` to see what would be added

## Security Notes

- Store `config.json` securely - it contains your password
- The script is added to `.gitignore` by default
- Authentication uses salted MD5 tokens (not plain text passwords in URLs)
- Consider using environment variables for sensitive data in production

## License

MIT License - Feel free to modify and use as needed!
