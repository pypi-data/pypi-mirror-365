#!/usr/bin/env python3
"""
Command line interface for NBA Summer League Headshots API
"""

import argparse
import sys
from .api import GLeagueAPI

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description='NBA Summer League 2025 Headshots API')
    parser.add_argument('--player', '-p', help='Get headshot path for a player')
    parser.add_argument('--team', '-t', help='List all players from a team')
    parser.add_argument('--search', '-s', help='Search for players by name')
    parser.add_argument('--list', '-l', action='store_true', help='List all available players')
    parser.add_argument('--download', '-d', nargs='+', help='Download headshots for specified players')
    parser.add_argument('--output', '-o', default='./downloaded_headshots', help='Output directory for downloads')
    
    args = parser.parse_args()
    
    if not any(vars(args).values()):
        parser.print_help()
        return
    
    api = GLeagueAPI()
    
    if args.player:
        headshot = api.get_player(args.player)
        if headshot:
            print(f"Headshot for {args.player}: {headshot}")
        else:
            print(f"No headshot found for {args.player}")
    
    if args.team:
        players = api.get_team(args.team)
        if players:
            print(f"\n{args.team} players ({len(players)} found):")
            for player in players:
                print(f"  - {player['name']}")
        else:
            print(f"No players found for {args.team}")
    
    if args.search:
        matches = api.search_players(args.search)
        if matches:
            print(f"\nPlayers matching '{args.search}' ({len(matches)} found):")
            for player in matches:
                print(f"  - {player}")
        else:
            print(f"No players found matching '{args.search}'")
    
    if args.list:
        players = api.list_all_players()
        print(f"\nAll available players ({len(players)} total):")
        for player in players:
            print(f"  - {player}")
    
    if args.download:
        result = api.batch_download(args.download, args.output)
        print(f"\nDownload complete:")
        print(f"  Downloaded: {result['total_found']} players")
        print(f"  Missing: {result['total_missing']} players")
        print(f"  Output directory: {result['output_dir']}")
        
        if result['not_found']:
            print(f"\nMissing players:")
            for player in result['not_found']:
                print(f"  - {player}")

if __name__ == '__main__':
    main()
