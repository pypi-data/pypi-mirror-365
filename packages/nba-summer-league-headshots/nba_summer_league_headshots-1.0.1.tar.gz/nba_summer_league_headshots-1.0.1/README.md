# NBA Summer League Headshots

Get NBA Summer League player headshots 

## Installation

```bash
pip install nba-summer-league-headshots
```

## Basic

```python
from nba_summer_league_headshots import get_headshot, get_headshots

# Get one player's headshot
image_path = get_headshot("Bronny James")
print(f"Saved to: {image_path}")

# Get multiple players' headshots  
players = ["Bronny James", "Dalton Knecht", "Reed Sheppard"]
result = get_headshots(players)
print(f"Downloaded: {result['total_found']} players to {result['output_dir']}")
```


## Advanced 


```python
from nba_summer_league_headshots import GLeagueAPI

api = GLeagueAPI()

# List all available players
all_players = api.list_all_players()
print(f"Total players: {len(all_players)}")

# Get all players from a specific team
hawks_players = api.get_team("Atlanta Hawks")
for player in hawks_players:
    print(f"{player['name']} - {player['team']}")

# Search for players by name
james_players = api.search_players("James")
print(f"Players with 'James': {james_players}")

# Copy individual headshots with custom directory
headshot_path = api.copy_headshot("Bronny James", "./my_custom_folder")

# Batch download multiple players' headshots
result = api.batch_download(["Bronny James", "Dalton Knecht"], output_dir="./my_custom_folder")

```


## Command Line

```bash
# Download player headshots
nba-headshots -d "Bronny James" "Dalton Knecht"

# Search players  
nba-headshots -s "James"

# List team players
nba-headshots -t "Atlanta Hawks"

# See all options
nba-headshots --help
```

## Example
```python
from nba_summer_league_headshots import GLeagueAPI

api = GLeagueAPI()

# List all available players
all_players = api.list_all_players()
result = api.batch_download(all_players, output_dir="./my_custom_folder")

```


## API Reference

### Simple Functions
- `get_headshot(player_name, output_dir="./headshots")` → Save one player's image
- `get_headshots(player_names, output_dir="./headshots")` → Save multiple players' images

### Advanced API (GLeagueAPI)
- `list_all_players()` → Get list of all players 
- `get_team(team_name)` → Get all players from a specific NBA team -> type: string
- `search_players(query)` → Find players by name -> type: string
- `copy_headshot(name, output_dir)` → Copy single player to custom directory -> type: string, output_dir: string
- `batch_download(names, output_dir)` → Download multiple with detailed results -> type: list, output_dir: string
