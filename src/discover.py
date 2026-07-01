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
    
    # Get music folders and their top-level directories
    print("\n" + "=" * 70)
    print("MUSIC FOLDERS & DIRECTORIES")
    print("=" * 70)
    try:
        response = client._make_request('getMusicFolders')
        folders = response.get('musicFolders', {}).get('musicFolder', [])
        if isinstance(folders, dict):
            folders = [folders]

        if folders:
            for folder in folders:
                folder_id = folder.get('id')
                print(f"\nFolder: {folder.get('name')} (ID: {folder_id})")
                # Get indexes (top-level artist/directory listing) for this folder
                try:
                    idx_response = client._make_request('getIndexes', {'musicFolderId': folder_id})
                    indexes = idx_response.get('indexes', {})
                    artist_list = []
                    for index in indexes.get('index', []):
                        artists = index.get('artist', [])
                        if isinstance(artists, dict):
                            artists = [artists]
                        artist_list.extend(artists)
                    if artist_list:
                        print(f"  Shows ({len(artist_list)} letter groups):")
                        for artist in artist_list:
                            group_id = artist.get('id')
                            group_name = artist.get('name')
                            # Drill into each letter group to get actual show directories
                            try:
                                dir_response = client.get_music_directory(group_id)
                                children = dir_response.get('child', [])
                                if isinstance(children, dict):
                                    children = [children]
                                dirs = [c for c in children if c.get('isDir')]
                                for d in dirs:
                                    print(f"    - {d.get('title', d.get('name'))} (ID: {d.get('id')})")
                            except Exception:
                                print(f"    [{group_name}] (ID: {group_id})")
                    else:
                        print("  No directories found")
                except Exception as e:
                    print(f"  Error fetching indexes: {e}")
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


def list_playlist(config_path: str = 'config.json'):
    """List current contents of the configured target playlist."""
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found.")
        return 1

    client = AirsonicClient(
        server_url=config['server_url'],
        username=config['username'],
        password=config['password'],
        api_version=config.get('api_version', '1.15.0'),
        client_name=config.get('client_name', 'PlaylistDiscovery')
    )

    if not client.ping():
        print("Error: Could not connect to Airsonic server or authentication failed.")
        return 1

    target_playlist_id = config.get('target_playlist_id')
    if not target_playlist_id:
        print("Error: 'target_playlist_id' not set in config.json")
        return 1

    playlists = client.get_playlists()
    playlist_name = next((p.get('name') for p in playlists if str(p.get('id')) == str(target_playlist_id)), target_playlist_id)

    playlist = client.get_playlist(target_playlist_id)
    entries = playlist.get('entry', [])
    if isinstance(entries, dict):
        entries = [entries]

    print(f"\nPlaylist: {playlist_name} (ID: {target_playlist_id}) -- {len(entries)} episodes\n")
    for i, entry in enumerate(entries, 1):
        title = entry.get('title', 'Unknown')
        duration = entry.get('duration', 0)
        mins, secs = divmod(duration, 60)
        print(f"  {i:>3}. {title} ({mins}:{secs:02d})")
    print()

    return 0


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Discover Airsonic folder and playlist IDs')
    parser.add_argument('--config', default='config.json', help='Path to config file')
    parser.add_argument('--list', action='store_true', help='List current playlist contents')

    args = parser.parse_args()

    if args.list:
        exit_code = list_playlist(args.config)
    else:
        exit_code = discover_ids(args.config)
    sys.exit(exit_code)
