# Airsonic Playlist Sync - systemd Configuration

## Installation (User Service)

For running as your user (recommended):

```bash
# 1. Copy service files
mkdir -p ~/.config/systemd/user
cp systemd/airsonic-sync-docker.service ~/.config/systemd/user/
cp systemd/airsonic-sync-docker.timer ~/.config/systemd/user/

# 2. Edit the service file to update the path
nano ~/.config/systemd/user/airsonic-sync-docker.service
# Change: WorkingDirectory=/path/to/airsonic-playlist-sync
# To your actual path

# 3. Reload systemd
systemctl --user daemon-reload

# 4. Enable and start the timer
systemctl --user enable airsonic-sync-docker.timer
systemctl --user start airsonic-sync-docker.timer

# 5. Enable linger (so it runs when you're not logged in)
loginctl enable-linger $USER
```

## Installation (System Service)

For running as a system service:

```bash
# 1. Copy service files
sudo cp systemd/airsonic-sync-docker.service /etc/systemd/system/
sudo cp systemd/airsonic-sync-docker.timer /etc/systemd/system/

# 2. Edit the service file to update paths and user
sudo nano /etc/systemd/system/airsonic-sync-docker.service
# Update WorkingDirectory and volume paths
# Add User= and Group= under [Service]

# 3. Reload systemd
sudo systemctl daemon-reload

# 4. Enable and start the timer
sudo systemctl enable airsonic-sync-docker.timer
sudo systemctl start airsonic-sync-docker.timer
```

## Management Commands

```bash
# Check timer status
systemctl --user status airsonic-sync-docker.timer

# List all timers
systemctl --user list-timers

# View logs
journalctl --user -u airsonic-sync-docker.service -f

# Manually trigger sync
systemctl --user start airsonic-sync-docker.service

# Stop timer
systemctl --user stop airsonic-sync-docker.timer

# Disable timer
systemctl --user disable airsonic-sync-docker.timer
```

## Customization

### Change Sync Interval

Edit the timer file:
```bash
nano ~/.config/systemd/user/airsonic-sync-docker.timer
```

Change `OnUnitActiveSec`:
```ini
OnUnitActiveSec=30min  # Every 30 minutes
OnUnitActiveSec=6h     # Every 6 hours
OnUnitActiveSec=1d     # Once per day
```

Then reload:
```bash
systemctl --user daemon-reload
systemctl --user restart airsonic-sync-docker.timer
```

### Environment Variables

Add environment variables to the service file:
```ini
[Service]
Environment="TZ=America/New_York"
Environment="SYNC_INTERVAL=3600"
```

## Troubleshooting

### Check if timer is active
```bash
systemctl --user is-active airsonic-sync-docker.timer
```

### View next run time
```bash
systemctl --user list-timers airsonic-sync-docker.timer
```

### Debug service
```bash
systemctl --user status airsonic-sync-docker.service
journalctl --user -u airsonic-sync-docker.service --since today
```

### Test service runs correctly
```bash
systemctl --user start airsonic-sync-docker.service
journalctl --user -u airsonic-sync-docker.service -f
```
