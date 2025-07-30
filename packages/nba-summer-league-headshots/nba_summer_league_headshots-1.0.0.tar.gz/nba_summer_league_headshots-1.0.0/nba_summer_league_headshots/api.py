#!/usr/bin/env python3
"""
NBA Summer League 2025 Player Headshot API

Provides programmatic access to 431+ verified NBA Summer League player headshots.
Supports individual lookups, team-based queries, and batch operations.
"""

import csv
from pathlib import Path
import shutil
from typing import List, Dict, Optional

class GLeagueAPI:
    """API for accessing NBA Summer League 2025 player headshots."""
    
    def __init__(self):
        """Initialize API with default paths to headshots and roster data."""
        package_dir = Path(__file__).parent
        self.headshots_dir = package_dir / 'NBA_Combined_Headshots'
        self.roster_file = package_dir / 'NBA_Roster_Clean.csv'
        self._load_roster()
    
    def _load_roster(self):
        """Load player roster data from CSV file."""
        self.players = []
        if self.roster_file.exists():
            with open(self.roster_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.players.append({
                        'name': row['Player'].strip(),
                        'team': row['Team'].strip(),
                        'clean_name': self._clean_name(row['Player'])
                    })
    
    def _clean_name(self, name: str) -> str:
        """Clean player name for file matching."""
        return name.replace(' ', '_').replace(',', '').replace('.', '').replace("'", "").replace('"', '')
    
    def _find_headshot(self, clean_name: str) -> Optional[Path]:
        """Find headshot file by clean name."""
        for ext in ['.jpg', '.png']:
            file_path = self.headshots_dir / f"{clean_name}{ext}"
            if file_path.exists():
                return file_path
        return None
    
    def get_player(self, name: str) -> Optional[str]:
        """
        Get path to player headshot image.
        
        Args:
            name: Player full name (e.g., "Javan Johnson")
            
        Returns:
            Absolute path to headshot file, or None if not found
        """
        clean_name = self._clean_name(name)
        headshot = self._find_headshot(clean_name)
        return str(headshot) if headshot else None
    
    def get_team(self, team_name: str) -> List[Dict]:
        """
        Get all players with headshots from specified team.
        
        Args:
            team_name: NBA team name (e.g., "Atlanta Hawks")
            
        Returns:
            List of player dictionaries with name, team, and headshot_path
        """
        team_players = []
        for player in self.players:
            if team_name.lower() in player['team'].lower():
                headshot = self._find_headshot(player['clean_name'])
                if headshot:
                    team_players.append({
                        'name': player['name'],
                        'team': player['team'],
                        'headshot_path': str(headshot)
                    })
        return team_players
    
    def batch_download(self, player_names: List[str], output_dir: str) -> Dict:
        """
        Download multiple player headshots to specified directory.
        
        Args:
            player_names: List of player names to download
            output_dir: Target directory for downloaded images
            
        Returns:
            Dictionary containing:
            - found: List of successfully downloaded players
            - not_found: List of players without available headshots
            - total_found: Count of successful downloads
            - total_missing: Count of missing players
            - output_dir: Path to output directory
        """
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        found = []
        not_found = []
        
        for name in player_names:
            headshot_path = self.get_player(name)
            if headshot_path:
                source = Path(headshot_path)
                dest = output_path / source.name
                shutil.copy2(source, dest)
                found.append({'name': name, 'file': str(dest)})
            else:
                not_found.append(name)
        
        return {
            'found': found,
            'not_found': not_found,
            'output_dir': str(output_path),
            'total_found': len(found),
            'total_missing': len(not_found)
        }
    
    def search_players(self, query: str) -> List[str]:
        """
        Search for players by name substring.
        
        Args:
            query: Search term to match against player names
            
        Returns:
            List of matching player names with available headshots
        """
        query = query.lower()
        matches = []
        for player in self.players:
            if query in player['name'].lower():
                if self._find_headshot(player['clean_name']):
                    matches.append(player['name'])
        return sorted(matches)
    
    def list_all_players(self) -> List[str]:
        """
        Get list of all players with available headshots.
        
        Returns:
            Sorted list of all player names with headshots
        """
        available = []
        for player in self.players:
            if self._find_headshot(player['clean_name']):
                available.append(player['name'])
        return sorted(available)
    
    def copy_headshot(self, name: str, output_dir: str = "./headshots") -> Optional[str]:
        """
        Copy a player's headshot to specified directory.
        
        Args:
            name: Player full name
            output_dir: Directory to copy the headshot to (default: "./headshots")
            
        Returns:
            Path to copied file, or None if player not found
        """
        headshot_path = self.get_player(name)
        if headshot_path:
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)
            
            source = Path(headshot_path)
            dest = output_path / source.name
            shutil.copy2(source, dest)
            return str(dest)
        return None

def get_headshot_path(player_name: str) -> Optional[str]:
    """
    Internal function to get player's headshot path in package directory.
    
    Args:
        player_name: Player full name
        
    Returns:
        Path to headshot file or None if not found
    """
    api = GLeagueAPI()
    return api.get_player(player_name)

def get_headshots(player_names: List[str], output_dir: str = "./headshots") -> Dict:
    """
    Get multiple player headshots and save them to your local directory.
    
    Args:
        player_names: List of player names to download
        output_dir: Directory to save images (default: "./headshots")
        
    Returns:
        Dictionary with download results
    """
    api = GLeagueAPI()
    return api.batch_download(player_names, output_dir)

def get_headshot(player_name: str, output_dir: str = "./headshots") -> Optional[str]:
    """
    Get a player's headshot and save it to your local directory.
    
    Args:
        player_name: Player full name
        output_dir: Directory to save the image (default: "./headshots")
        
    Returns:
        Path to saved file or None if player not found
    """
    api = GLeagueAPI()
    return api.copy_headshot(player_name, output_dir)

# Example usage
if __name__ == "__main__":
    api = GLeagueAPI()
    
    # Single player
    print("Getting Javan Johnson's headshot...")
    javan = api.get_player("Javan Johnson")
    print(f"Javan Johnson: {javan}")
    
    # Team players
    print("\nAtlanta Hawks players...")
    hawks = api.get_team("Atlanta Hawks")
    for player in hawks[:3]:
        print(f"  {player['name']}: {player['headshot_path']}")
    
    # Batch download
    print("\nBatch downloading 3 players...")
    players = ["Javan Johnson", "Ben Gregg", "Dwight Murray, Jr."]
    result = api.batch_download(players, "./test_download")
    print(f"Downloaded {result['total_found']} players to {result['output_dir']}")
