# Container Usage Examples

## Quick Start with Docker

### 1. One-Time Run
```bash
# Build and run once
make run

# Or manually
docker build -t airsonic-playlist-sync:latest .
docker run --rm \
  -v "$(pwd)/config.json:/config/config.json:ro" \
  -v "$(pwd)/logs:/app/logs" \
  airsonic-playlist-sync:latest
```

### 2. Scheduled Background Sync
```bash
# Start container that syncs every hour
make up

# View logs in real-time
make logs

# Stop when done
make down
```

### 3. Discovery
```bash
# Find your folder and playlist IDs
make discover
```

## Advanced Usage

### Custom Sync Interval

Edit `docker-compose.scheduled.yml`:
```yaml
environment:
  - SYNC_INTERVAL=900  # Sync every 15 minutes
```

Or set it when starting:
```bash
SYNC_INTERVAL=1800 docker-compose -f docker-compose.scheduled.yml up -d
```

### Using Podman Instead of Docker

Works identically - just replace `docker` with `podman`:
```bash
podman build -t airsonic-playlist-sync:latest .
podman run --rm \
  -v "$(pwd)/config.json:/config/config.json:ro" \
  airsonic-playlist-sync:latest
```

### Running in Kubernetes

Example Pod definition:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: airsonic-sync
spec:
  containers:
  - name: sync
    image: airsonic-playlist-sync:latest
    volumeMounts:
    - name: config
      mountPath: /config/config.json
      subPath: config.json
      readOnly: true
  volumes:
  - name: config
    secret:
      secretName: airsonic-config
  restartPolicy: OnFailure
```

Create secret:
```bash
kubectl create secret generic airsonic-config \
  --from-file=config.json=./config.json
```

### Running with docker-compose on Schedule

For systems without cron (like Windows), use the scheduled compose file:
```bash
# Start (syncs every hour by default)
docker-compose -f docker-compose.scheduled.yml up -d

# Change interval to 30 minutes
# Edit docker-compose.scheduled.yml: SYNC_INTERVAL=1800

# Restart to apply changes
docker-compose -f docker-compose.scheduled.yml restart
```

## Troubleshooting

### Container can't connect to Airsonic
- Check your `config.json` credentials
- Ensure the server URL is accessible from within the container
- If using localhost, try using your machine's IP or hostname instead

### Permission errors with volumes
```bash
# Ensure config.json is readable
chmod 644 config.json

# Create logs directory with proper permissions
mkdir -p logs
chmod 755 logs
```

### View container logs
```bash
# For one-time runs (if using --name)
docker logs airsonic-playlist-sync

# For scheduled runs
docker-compose -f docker-compose.scheduled.yml logs -f
```

### Rebuild after code changes
```bash
# Clear cache and rebuild
docker build --no-cache -t airsonic-playlist-sync:latest .

# Or using make
make clean
make build
```
