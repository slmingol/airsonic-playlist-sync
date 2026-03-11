#!/bin/bash
# Quick setup script for Airsonic Playlist Sync

echo "==================================================================="
echo "  Airsonic Playlist Sync - Setup"
echo "==================================================================="
echo

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed."
    echo "Please install Python 3 and try again."
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"
echo

# Check if pip is installed
if ! command -v pip3 &> /dev/null && ! python3 -m pip --version &> /dev/null; then
    echo "Error: pip is not installed."
    echo "Please install pip and try again."
    exit 1
fi

echo "✓ pip found"
echo

# Install dependencies
echo "Installing dependencies..."
python3 -m pip install -r requirements.txt --user
echo

# Check if config.json exists
if [ -f "config.json" ]; then
    echo "✓ config.json already exists"
else
    echo "Creating config.json from template..."
    cp config.example.json config.json
    echo "⚠ Please edit config.json with your Airsonic credentials"
    echo
    
    # Try to open config.json in editor
    if command -v nano &> /dev/null; then
        read -p "Would you like to edit config.json now? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            nano config.json
        fi
    fi
fi

echo
echo "==================================================================="
echo "  Setup Complete!"
echo "==================================================================="
echo
echo "Next steps:"
echo "  1. Make sure config.json has your Airsonic credentials"
echo "  2. Run: python3 src/discover.py"
echo "     This will show you available folders and playlists"
echo "  3. Add the IDs to config.json:"
echo "     - source_directory_id"
echo "     - target_playlist_id"
echo "  4. Test with: python3 src/sync_playlist.py --dry-run"
echo "  5. Run for real: python3 src/sync_playlist.py"
echo
echo "See docs/README.md for more information."
echo
