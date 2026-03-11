#!/usr/bin/env python3
"""
Airsonic Playlist Sync Script
Automatically adds new music from a shared folder to a playlist.
"""

import json
import hashlib
import random
import string
import urllib.parse
import requests
import sys
import re
from datetime import datetime
from typing import Dict, List, Set, Optional


class AirsonicClient:
    """Client for interacting with Airsonic-Advanced API."""
    
    def __init__(self, server_url: str, username: str, password: str, 
                 api_version: str = "1.15.0", client_name: str = "PlaylistSync"):
        self.server_url = server_url.rstrip('/')
        self.username = username
        self.password = password
        self.api_version = api_version
        self.client_name = client_name
        
    def _generate_salt(self, length: int = 12) -> str:
        """Generate a random salt for authentication."""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    def _generate_token(self, password: str, salt: str) -> str:
        """Generate authentication token using MD5(password + salt)."""
        token_string = password + salt
        return hashlib.md5(token_string.encode('utf-8')).hexdigest()
    
    def _get_auth_params(self) -> Dict[str, str]:
        """Get authentication parameters for API calls."""
        salt = self._generate_salt()
        token = self._generate_token(self.password, salt)
        
        return {
            'u': self.username,
            't': token,
            's': salt,
            'v': self.api_version,
            'c': self.client_name,
            'f': 'json'
        }
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make an API request to Airsonic."""
        if params is None:
            params = {}
        
        # Add authentication parameters
        params.update(self._get_auth_params())
        
        url = f"{self.server_url}/rest/{endpoint}"
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Check Airsonic response status
            subsonic_response = data.get('subsonic-response', {})
            server_version = subsonic_response.get('version', 'unknown')
            
            if subsonic_response.get('status') != 'ok':
                error = subsonic_response.get('error', {})
                error_code = error.get('code', 'unknown')
                error_msg = error.get('message', 'Unknown error')
                raise Exception(f"API Error (code {error_code}): {error_msg} [Server v{server_version}, Client v{self.api_version}]")
            
            return subsonic_response
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {e}")
    
    def ping(self) -> bool:
        """Test server connectivity and authentication."""
        try:
            response = self._make_request('ping')
            return response.get('status') == 'ok'
        except Exception as e:
            print(f"Ping failed: {e}")
            return False
    
    def get_shares(self) -> List[Dict]:
        """Get all shares for the user."""
        response = self._make_request('getShares')
        shares = response.get('shares', {}).get('share', [])
        
        # Ensure shares is always a list
        if isinstance(shares, dict):
            shares = [shares]
        
        return shares
    
    def get_share_by_id(self, share_id: str) -> Optional[Dict]:
        """Get a specific share by its ID."""
        shares = self.get_shares()
        for share in shares:
            if share.get('id') == share_id:
                return share
        return None
    
    def get_music_directory(self, directory_id: str) -> Dict:
        """Get contents of a music directory."""
        response = self._make_request('getMusicDirectory', {'id': directory_id})
        return response.get('directory', {})
    
    def get_playlist(self, playlist_id: str) -> Dict:
        """Get a playlist with all its songs."""
        response = self._make_request('getPlaylist', {'id': playlist_id})
        return response.get('playlist', {})
    
    def get_playlists(self) -> List[Dict]:
        """Get all playlists."""
        response = self._make_request('getPlaylists')
        playlists = response.get('playlists', {}).get('playlist', [])
        
        # Ensure playlists is always a list
        if isinstance(playlists, dict):
            playlists = [playlists]
        
        return playlists
    
    def update_playlist(self, playlist_id: str, song_ids_to_add: List[str] = None,
                       song_indices_to_remove: List[int] = None, 
                       name: str = None, comment: str = None, public: bool = None) -> bool:
        """Update a playlist by adding/removing songs or changing metadata."""
        params = {'playlistId': playlist_id}
        
        if name:
            params['name'] = name
        if comment:
            params['comment'] = comment
        if public is not None:
            params['public'] = str(public).lower()
        
        # Add multiple songIdToAdd parameters
        if song_ids_to_add:
            for song_id in song_ids_to_add:
                if 'songIdToAdd' not in params:
                    params['songIdToAdd'] = []
                params['songIdToAdd'].append(song_id)
        
        # Add multiple songIndexToRemove parameters  
        if song_indices_to_remove:
            for index in song_indices_to_remove:
                if 'songIndexToRemove' not in params:
                    params['songIndexToRemove'] = []
                params['songIndexToRemove'].append(str(index))
        
        try:
            self._make_request('updatePlaylist', params)
            return True
        except Exception as e:
            print(f"Failed to update playlist: {e}")
            return False
    
    def add_songs_to_playlist(self, playlist_id: str, song_ids: List[str]) -> bool:
        """Add multiple songs to a playlist."""
        return self.update_playlist(playlist_id, song_ids_to_add=song_ids)


def get_all_songs_from_directory(client: AirsonicClient, directory_id: str, 
                                  recursive: bool = True) -> List[Dict]:
    """
    Get all songs from a directory, optionally recursing into subdirectories.
    """
    all_songs = []
    
    directory = client.get_music_directory(directory_id)
    children = directory.get('child', [])
    
    # Ensure children is always a list
    if isinstance(children, dict):
        children = [children]
    
    for child in children:
        if child.get('isDir'):
            # It's a directory, recurse if enabled
            if recursive:
                all_songs.extend(get_all_songs_from_directory(client, child['id'], recursive))
        else:
            # It's a song
            all_songs.append(child)
    
    return all_songs


def sync_folder_to_playlist(config_path: str = 'config.json', dry_run: bool = False, max_songs: int = 15):
    """
    Main function to sync songs from a folder to a playlist.
    
    Args:
        config_path: Path to configuration file
        dry_run: If True, show what would be done without making changes
        max_songs: Maximum number of most recent songs to keep in playlist (default: 15)
    """
    # Load configuration
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found.")
        print("Please create it based on config.example.json")
        return 1
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in configuration file: {e}")
        return 1
    
    # Initialize client
    client = AirsonicClient(
        server_url=config['server_url'],
        username=config['username'],
        password=config['password'],
        api_version=config.get('api_version', '1.15.0'),
        client_name=config.get('client_name', 'PlaylistSync')
    )
    
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting playlist sync...")
    
    # Test connection
    print("Testing connection...", end=' ')
    if not client.ping():
        print("FAILED")
        print("Error: Could not connect to Airsonic server or authentication failed.")
        return 1
    print("OK")
    
    # Get shares to find the actual IDs
    print("Fetching shares...", end=' ')
    shares = client.get_shares()
    
    source_share_id = config.get('source_share_id')
    target_share_id = config.get('target_playlist_share_id')
    
    # Find the source directory ID from share
    source_dir_id = None
    target_playlist_id = None
    
    for share in shares:
        share_id = share.get('id')
        if share_id == source_share_id:
            # Share entry could contain multiple items, get the first
            entries = share.get('entry', [])
            if isinstance(entries, dict):
                entries = [entries]
            if entries:
                source_dir_id = entries[0].get('id')
        elif share_id == target_share_id:
            # For playlist shares
            entries = share.get('entry', [])
            if isinstance(entries, dict):
                entries = [entries]
            # We need the playlist ID, not the song IDs
            # Try to get it from the share URL or query all playlists
            pass
    
    print(f"Found {len(shares)} shares")
    
    # If we didn't find IDs from shares, try alternative approach
    # For playlists, query all playlists and match by name or search
    if not target_playlist_id:
        print("Fetching playlists...", end=' ')
        playlists = client.get_playlists()
        print(f"Found {len(playlists)} playlists")
        
        # If a playlist_name or playlist_id is in config, use that
        if 'target_playlist_id' in config:
            target_playlist_id = config['target_playlist_id']
        elif 'target_playlist_name' in config:
            target_name = config['target_playlist_name']
            for playlist in playlists:
                if playlist.get('name') == target_name:
                    target_playlist_id = playlist.get('id')
                    break
        
        # If still not found, list playlists for user
        if not target_playlist_id:
            print("\nAvailable playlists:")
            for i, playlist in enumerate(playlists, 1):
                print(f"  {i}. {playlist.get('name')} (ID: {playlist.get('id')})")
            print("\nPlease add 'target_playlist_id' to your config.json")
            return 1
    
    # Similar for source directory
    if not source_dir_id and 'source_directory_id' in config:
        source_dir_id = config['source_directory_id']
    
    if not source_dir_id:
        print("\nError: Could not determine source directory ID.")
        print("Please add 'source_directory_id' to your config.json")
        return 1
    
    print(f"Source directory ID: {source_dir_id}")
    print(f"Target playlist ID: {target_playlist_id}")
    
    # Get all songs from source directory
    print("Fetching songs from source directory...", end=' ')
    source_songs = get_all_songs_from_directory(client, source_dir_id, recursive=True)
    print(f"Found {len(source_songs)} songs")
    
    # Get current playlist contents
    print("Fetching current playlist...", end=' ')
    playlist = client.get_playlist(target_playlist_id)
    playlist_entries = playlist.get('entry', [])
    if isinstance(playlist_entries, dict):
        playlist_entries = [playlist_entries]
    print(f"Contains {len(playlist_entries)} songs")
    
    # Helper function to extract date from title for sorting
    def get_sort_key(song):
        """Extract date from title (YYYYMMDD format) or fall back to created date."""
        title = song.get('title', '')
        # Look for YYYYMMDD pattern in title
        date_match = re.search(r'(\d{8})', title)
        if date_match:
            return date_match.group(1)
        # Fall back to created date or title
        return song.get('created', title)
    
    # Sort ALL source songs by date (newest first) and keep only top N
    all_songs_sorted = sorted(source_songs, key=get_sort_key, reverse=True)
    top_songs = all_songs_sorted[:max_songs]
    top_song_ids = {song['id'] for song in top_songs}
    
    print(f"\nTop {len(top_songs)} most recent episodes:")
    existing_song_ids = {entry['id'] for entry in playlist_entries}
    for song in top_songs:
        artist = song.get('artist', 'Unknown')
        title = song.get('title', song.get('name', 'Unknown'))
        date_key = get_sort_key(song)
        in_playlist = "✓" if song['id'] in existing_song_ids else " "
        print(f"  [{in_playlist}] {date_key} - {artist} - {title}")
    
    # Find songs to add (in top 15 but not in current playlist)
    songs_to_add = [song for song in top_songs if song['id'] not in existing_song_ids]
    
    # Find songs to remove (in playlist but not in top 15)
    indices_to_remove = []
    for idx, entry in enumerate(playlist_entries):
        if entry['id'] not in top_song_ids:
            indices_to_remove.append(idx)
    
    if not songs_to_add and not indices_to_remove:
        print(f"\n✓ Playlist already contains exactly the top {max_songs} most recent episodes!")
        return 0
    
    print(f"\nChanges:")
    if songs_to_add:
        print(f"  Add {len(songs_to_add)} new song(s)")
    if indices_to_remove:
        print(f"  Remove {len(indices_to_remove)} old song(s)")
    
    if dry_run:
        print(f"\n[DRY RUN] Would update playlist to maintain {max_songs} most recent episodes.")
        return 0
    
    # Update playlist
    print(f"\nUpdating playlist...", end=' ')
    song_ids_to_add = [song['id'] for song in songs_to_add] if songs_to_add else None
    
    if client.update_playlist(target_playlist_id, 
                             song_ids_to_add=song_ids_to_add,
                             song_indices_to_remove=indices_to_remove if indices_to_remove else None):
        print("SUCCESS")
        print(f"\n✓ Playlist now contains the {max_songs} most recent episodes")
        return 0
    else:
        print("FAILED")
        return 1


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Sync Airsonic folder to playlist')
    parser.add_argument('--config', default='config.json', help='Path to config file')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')
    parser.add_argument('--max-songs', type=int, default=15, help='Maximum number of most recent songs to keep in playlist (default: 15)')
    
    args = parser.parse_args()
    
    exit_code = sync_folder_to_playlist(args.config, args.dry_run, args.max_songs)
    sys.exit(exit_code)
