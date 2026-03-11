# Quick Start Guide

Choose your preferred method: **Native Python** or **Docker Container**

---

## 🐍 Native Python (Traditional)

### Setup
```bash
# 1. Run setup script
./setup.sh

# 2. Edit config.json with your credentials
nano config.json

# 3. Discover IDs
python3 discover.py

# 4. Add IDs to config.json
nano config.json

# 5. Test
python3 sync_playlist.py --dry-run

# 6. Run
python3 sync_playlist.py

# 7. Automate (optional)
./setup-cron.sh
```

**Pros:**
- Faster execution (no container overhead)
- Direct access to Python environment
- Easy to debug

**Cons:**
- Requires Python installed
- Dependencies on host system
- May have version conflicts

---

## 🐳 Docker Container (Recommended for Production)

### Setup
```bash
# 1. Create config
cp config.example.json config.json
nano config.json

# 2. Discover IDs
make discover
# or: ./run-docker-discover.sh

# 3. Add IDs to config.json
nano config.json

# 4. Test
make run-dry
# or: ./run-docker.sh --dry-run

# 5. Run once
make run
# or: ./run-docker.sh

# 6. Run on schedule (every hour)
make up

# 7. View logs
make logs

# 8. Stop scheduled sync
make down
```

**Pros:**
- Isolated environment
- No Python installation needed
- Consistent across systems
- Easy to deploy/scale
- Works with orchestration (K8s, Swarm)

**Cons:**
- Requires Docker
- Slightly slower startup
- Extra disk space for image

---

## 🚀 Super Quick Start (Docker)

If you already have your credentials:

```bash
# 1. Create config.json
cat > config.json << 'EOF'
{
  "server_url": "https://airsonic-advanced.lamolabs.org",
  "username": "YOUR_USERNAME",
  "password": "YOUR_PASSWORD",
  "api_version": "1.16.1",
  "client_name": "PlaylistSync"
}
EOF

# 2. Find your IDs
make discover

# 3. Add to config.json:
#    "source_directory_id": "...",
#    "target_playlist_id": "..."

# 4. Start automatic sync
make up
```

Done! Your playlist will sync every hour.

---

## 📋 Common Tasks

| Task | Native Python | Docker |
|------|---------------|--------|
| One-time sync | `python3 sync_playlist.py` | `make run` |
| Dry run | `python3 sync_playlist.py --dry-run` | `make run-dry` |
| Find IDs | `python3 discover.py` | `make discover` |
| Schedule hourly | `./setup-cron.sh` | `make up` |
| View logs | `tail -f sync.log` | `make logs` |
| Stop scheduler | Remove from cron | `make down` |

---

## 🔧 Configuration

Your `config.json` should look like:

```json
{
  "server_url": "https://airsonic-advanced.lamolabs.org",
  "username": "admin",
  "password": "your_password",
  "api_version": "1.16.1",
  "client_name": "PlaylistSync",
  "source_directory_id": "12345",
  "target_playlist_id": "67890"
}
```

### Finding IDs

The discovery tool shows:
- **Shares** - Your shared folders/playlists
- **Playlists** - All playlists (use the ID)
- **Music Folders** - Top-level folders

Copy the relevant IDs to your config.

---

## ⏰ Scheduling Options

### Option 1: Cron (Native)
```bash
./setup-cron.sh  # Interactive setup
```

### Option 2: Docker Scheduled
```bash
make up  # Runs every hour
```

To change interval, edit `docker-compose.scheduled.yml`:
```yaml
environment:
  - SYNC_INTERVAL=1800  # 30 minutes
```

### Option 3: Manual Cron + Docker
```bash
# Edit crontab
crontab -e

# Add line (every hour):
0 * * * * cd /path/to/airsonic-playlist-sync && ./run-docker.sh
```

---

## 🆘 Troubleshooting

### "Authentication failed"
- Check username/password in config.json
- Verify server URL is correct
- Try logging in via web interface

### "Can't find folder/playlist"
- Run discovery: `make discover` or `python3 discover.py`
- Check you're logged in as correct user
- Verify shares haven't expired

### "No new songs found"
- Songs may already be in playlist
- Check source directory has music files
- Run with `--dry-run` to see details

### Docker: "Cannot connect to server"
- If using `localhost`, try your machine's IP
- Check server is accessible from container
- Verify no firewall blocking

---

## 📚 More Information

- [README.md](README.md) - Full documentation
- [DOCKER.md](DOCKER.md) - Advanced Docker usage
- `make help` - Show all make commands

---

## 🎯 Recommended Workflow

1. **Development/Testing**: Use native Python with `--dry-run`
2. **Production**: Use Docker with scheduled runs
3. **Quick checks**: Use `make run-dry`
4. **Monitoring**: Use `make logs` or check log files

Happy syncing! 🎵
