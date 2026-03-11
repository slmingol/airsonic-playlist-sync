#!/bin/bash
# Helper script to set up automated sync via cron

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
SYNC_SCRIPT="$PROJECT_DIR/src/sync_playlist.py"
LOG_FILE="$PROJECT_DIR/sync.log"

echo "==================================================================="
echo "  Airsonic Playlist Sync - Cron Setup"
echo "==================================================================="
echo
echo "This will help you set up automatic playlist syncing."
echo "Current directory: $SCRIPT_DIR"
echo

# Menu for frequency
echo "How often do you want to sync?"
echo "  1) Every 15 minutes"
echo "  2) Every 30 minutes"
echo "  3) Every hour"
echo "  4) Every 6 hours"
echo "  5) Once per day (at midnight)"
echo "  6) Custom cron expression"
echo

read -p "Enter your choice (1-6): " choice

case $choice in
    1)
        CRON_SCHEDULE="*/15 * * * *"
        DESCRIPTION="every 15 minutes"
        ;;
    2)
        CRON_SCHEDULE="*/30 * * * *"
        DESCRIPTION="every 30 minutes"
        ;;
    3)
        CRON_SCHEDULE="0 * * * *"
        DESCRIPTION="every hour"
        ;;
    4)
        CRON_SCHEDULE="0 */6 * * *"
        DESCRIPTION="every 6 hours"
        ;;
    5)
        CRON_SCHEDULE="0 0 * * *"
        DESCRIPTION="once per day at midnight"
        ;;
    6)
        read -p "Enter custom cron expression: " CRON_SCHEDULE
        DESCRIPTION="with custom schedule"
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

echo
echo "==================================================================="
echo "  Cron Job Configuration"
echo "==================================================================="
echo
echo "Schedule: $DESCRIPTION"
echo "Cron expression: $CRON_SCHEDULE"
echo
echo "The following line will be added to your crontab:"
echo
echo "$CRON_SCHEDULE cd $SCRIPT_DIR && /usr/bin/python3 $SYNC_SCRIPT >> $LOG_FILE 2>&1"
echo
read -p "Do you want to add this to your crontab? (y/n) " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Add to crontab
    (crontab -l 2>/dev/null; echo "$CRON_SCHEDULE cd $SCRIPT_DIR && /usr/bin/python3 $SYNC_SCRIPT >> $LOG_FILE 2>&1") | crontab -
    
    echo
    echo "✓ Cron job added successfully!"
    echo
    echo "Your playlist will now sync $DESCRIPTION"
    echo "Logs will be written to: $LOG_FILE"
    echo
    echo "To view your crontab: crontab -l"
    echo "To edit your crontab: crontab -e"
    echo "To remove this cron job: crontab -e (and delete the line)"
    echo
else
    echo
    echo "Cron job not added. You can add it manually later:"
    echo "  1. Run: crontab -e"
    echo "  2. Add this line:"
    echo "     $CRON_SCHEDULE cd $SCRIPT_DIR && /usr/bin/python3 $SYNC_SCRIPT >> $LOG_FILE 2>&1"
    echo
fi
