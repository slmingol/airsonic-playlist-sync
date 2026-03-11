#!/usr/bin/env python3
"""
Helper script to discover Airsonic folder and playlist IDs.
"""

__version__ = "1.0.0"

import json
import sys
from sync_playlist import AirsonicClient


def discover_ids(config_path: str = 'config.json'):
    """Discover and display available folders and playlists."""
    
    # Load configuration
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found.")
        print("Please create config.json with your server URL, username, and password")
        return 1
    
    # Initialize client
    client = AirsonicClient(
        server_url=config['server_url'],
        username=config['username'],
        password=config['password'],
        api_version=config.get('api_version', '1.15.0'),
        client_name=config.get('client_name', 'PlaylistDiscovery')
    )
    
    print("Testing connection...", end=' ')
    if not client.ping():
        print("FAILED")
        print("Error: Could not connect to Airsonic server or authentication failed.")
        return 1
    print("OK\n")
    
    # Get shares
    print("=" * 70)
    print("SHARES")
    print("=" * 70)
    try:
        shares = client.get_shares()
        if shares:
            for share in shares:
                print(f"\nShare: {share.get('description', 'No description')}")
                print(f"  ID: {share.get('id')}")
                print(f"  URL: {share.get('url')}")
                print(f"  Created: {share.get('created')}")
                
                entries = share.get('entry', [])
                if isinstance(entries, dict):
                    entries = [entries]
                
                if entries:
                    print(f"  Contains {len(entries)} item(s):")
                    for entry in entries[:5]:  # Show first 5
                        is_dir = entry.get('isDir', False)
                        item_type = 'Directory' if is_dir else 'Song'
                        print(f"    - [{item_type}] {entry.get('title', entry.get('name', 'Unknown'))} (ID: {entry.get('id')})")
                    if len(entries) > 5:
                        print(f"    ... and {len(entries) - 5} more items")
        else:
            print("No shares found")
    except Exception as e:
        print(f"Error fetching shares: {e}")
    
    # Get playlists
    print("\n" + "=" * 70)
    print("PLAYLISTS")
    print("=" * 70)
    try:
        playlists = client.get_playlists()
        if playlists:
            for playlist in playlists:
                print(f"\nPlaylist: {playlist.get('name')}")
                print(f"  ID: {playlist.get('id')}")
                print(f"  Owner: {playlist.get('owner')}")
                print(f"  Song Count: {playlist.get('songCount', 0)}")
                print(f"  Duration: {playlist.get('duration', 0)}s")
                print(f"  Public: {playlist.get('public', False)}")
        else:
            print("No playlists found")
    except Exception as e:
        print(f"Error fetching playlists: {e}")
    
    # Get music folders
    print("\n" + "=" * 70)
    print("MUSIC FOLDERS")
    print("=" * 70)
    try:
        response = client._make_request('getMusicFolders')
        folders = response.get('musicFolders', {}).get('musicFolder', [])
        if isinstance(folders, dict):
            folders = [folders]
        
        if folders:
            for folder in folders:
                print(f"\nFolder: {folder.get('name')}")
                print(f"  ID: {folder.get('id')}")
        else:
            print("No music folders found")
    except Exception as e:
        print(f"Error fetching music folders: {e}")
    
    print("\n" + "=" * 70)
    print("\nTo use these in your config.json, add:")
    print("  'source_directory_id': 'ID_FROM_SHARES_OR_FOLDERS'")
    print("  'target_playlist_id': 'ID_FROM_PLAYLISTS'")
    print()
    
    return 0


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Discover Airsonic folder and playlist IDs')
    parser.add_argument('--config', default='config.json', help='Path to config file')
    
    args = parser.parse_args()
    
    exit_code = discover_ids(args.config)
    sys.exit(exit_code)
