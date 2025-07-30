"""
Poker game data analysis module.

This module provides comprehensive analysis tools for poker game data,
including equity evolution, hand progression tracking, and pattern recognition.
"""

import json
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import statistics
from collections import defaultdict, Counter
import glob
import sys


@dataclass
class PlayerHandData:
    """Represents a player's hand data for a specific street."""
    player_id: int
    hole_cards: List[str]
    hand_type: str
    hand_weight: int
    equity: float
    winner: bool


@dataclass
class GameData:
    """Represents a complete game with all streets and player data."""
    game_id: int
    board_flop: List[str]
    board_turn: List[str]
    board_river: List[str]
    winners_flop: List[str]
    winners_turn: List[str]
    winners_river: List[str]
    winning_hand_flop: Dict[str, Any]
    winning_hand_turn: Dict[str, Any]
    winning_hand_river: Dict[str, Any]
    player_hands: List[PlayerHandData]


@dataclass
class EquityChange:
    """Represents equity change for a player between streets."""
    player_id: int
    flop_to_turn: float
    turn_to_river: float
    flop_to_river: float
    volatility: float


@dataclass
class HandProgression:
    """Represents hand type progression for a player."""
    player_id: int
    flop_hand: str
    turn_hand: str
    river_hand: str
    improved: bool
    degraded: bool


class GameDataLoader:
    """Loads and parses poker game data from JSON files in a directory."""
    
    def __init__(self, directory_path: str, pattern: str = "*.json"):
        """Initialize with path to directory containing game data files."""
        self.directory_path = Path(directory_path)
        self.pattern = pattern
        self.all_raw_data: List[Dict[str, Any]] = []
        self.combined_raw_data: Dict[str, Any] = {}
        self.games: List[GameData] = []
        self.processed_files: List[str] = []
        self.failed_files: List[str] = []
    
    def discover_files(self) -> List[Path]:
        """Discover all JSON files in the directory matching the pattern."""
        if not self.directory_path.exists():
            print(f"Error: Directory {self.directory_path} does not exist")
            return []
        
        if not self.directory_path.is_dir():
            print(f"Error: {self.directory_path} is not a directory")
            return []
        
        # Use glob to find matching files
        pattern_path = self.directory_path / self.pattern
        files = list(self.directory_path.glob(self.pattern))
        
        if not files:
            print(f"No files found matching pattern '{self.pattern}' in {self.directory_path}")
            return []
        
        return sorted(files)
    
    def load_data(self, verbose: bool = False) -> bool:
        """Load raw JSON data from all matching files in directory."""
        files = self.discover_files()
        if not files:
            return False
        
        self.all_raw_data = []
        self.processed_files = []
        self.failed_files = []
        
        if verbose:
            print(f"Found {len(files)} files to process...")
        
        for i, file_path in enumerate(files, 1):
            if verbose:
                print(f"Processing file {i}/{len(files)}: {file_path.name}")
            
            try:
                with open(file_path, 'r') as f:
                    file_data = json.load(f)
                    self.all_raw_data.append(file_data)
                    self.processed_files.append(str(file_path))
            except (FileNotFoundError, json.JSONDecodeError) as e:
                if verbose:
                    print(f"  Error loading {file_path.name}: {e}")
                self.failed_files.append(str(file_path))
                continue
        
        if not self.all_raw_data:
            print("Error: No files could be loaded successfully")
            return False
        
        # Combine all data into a single structure
        self._combine_data()
        
        if verbose:
            print(f"Successfully processed {len(self.processed_files)} files")
            if self.failed_files:
                print(f"Failed to process {len(self.failed_files)} files")
        
        return True
    
    def _combine_data(self) -> None:
        """Combine data from all files into a single structure."""
        combined_games = []
        combined_metadata: Dict[str, Any] = {}
        game_id_counter = 1
        
        for file_data in self.all_raw_data:
            # Use metadata from first file, but track differences
            if not combined_metadata and 'simulation_metadata' in file_data:
                combined_metadata = file_data['simulation_metadata'].copy()
            
            # Add all games with renumbered IDs to avoid conflicts
            for game in file_data.get('games', []):
                game_copy = game.copy()
                game_copy['id'] = game_id_counter
                combined_games.append(game_copy)
                game_id_counter += 1
        
        self.combined_raw_data = {
            'simulation_metadata': combined_metadata,
            'games': combined_games
        }
    
    def parse_games(self) -> List[GameData]:
        """Parse combined raw data into structured GameData objects."""
        if not self.combined_raw_data:
            return []
        
        self.games = []
        for game_raw in self.combined_raw_data.get('games', []):
            player_hands = []
            
            for player_data in game_raw.get('player_hands', []):
                # Extract data for each street
                flop_data = player_data.get('flop', {})
                turn_data = player_data.get('turn', {})
                river_data = player_data.get('river', {})
                
                # Create PlayerHandData with all street information
                player_hand = PlayerHandData(
                    player_id=player_data['player_id'],
                    hole_cards=player_data['hole_cards'],
                    hand_type=river_data.get('hand_type', ''),
                    hand_weight=river_data.get('hand_weight', 0),
                    equity=river_data.get('equity', 0.0),
                    winner=river_data.get('winner', False)
                )
                player_hands.append(player_hand)
            
            game = GameData(
                game_id=game_raw['id'],
                board_flop=game_raw['board_at_flop'],
                board_turn=game_raw['board_at_turn'],
                board_river=game_raw['board_at_river'],
                winners_flop=game_raw['winners_flop'],
                winners_turn=game_raw['winners_turn'],
                winners_river=game_raw['winners_river'],
                winning_hand_flop=game_raw['winning_hand_flop'],
                winning_hand_turn=game_raw['winning_hand_turn'],
                winning_hand_river=game_raw['winning_hand_river'],
                player_hands=player_hands
            )
            self.games.append(game)
        
        return self.games
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get combined simulation metadata."""
        if not self.combined_raw_data:
            return {}
        
        base_metadata = self.combined_raw_data.get('simulation_metadata', {})
        if base_metadata is None:
            base_metadata = {}
        
        metadata: Dict[str, Any] = base_metadata.copy()
        
        # Add information about the batch processing
        metadata['total_files_processed'] = len(self.processed_files)
        metadata['total_files_failed'] = len(self.failed_files)
        metadata['total_games'] = len(self.combined_raw_data.get('games', []))
        
        return metadata


class EquityAnalyzer:
    """Analyzes equity changes across streets."""
    
    def __init__(self, games: List[GameData], raw_data: Dict[str, Any]):
        """Initialize with parsed game data and raw data."""
        self.games = games
        self.raw_data = raw_data
        self.equity_changes: List[EquityChange] = []
    
    def calculate_equity_changes(self) -> List[EquityChange]:
        """Calculate equity changes for all players across all games."""
        self.equity_changes = []
        
        for game_raw in self.raw_data.get('games', []):
            for player_data in game_raw.get('player_hands', []):
                flop_equity = player_data.get('flop', {}).get('equity', 0.0)
                turn_equity = player_data.get('turn', {}).get('equity', 0.0)
                river_equity = player_data.get('river', {}).get('equity', 0.0)
                
                flop_to_turn = turn_equity - flop_equity
                turn_to_river = river_equity - turn_equity
                flop_to_river = river_equity - flop_equity
                
                # Calculate volatility as sum of absolute changes
                volatility = abs(flop_to_turn) + abs(turn_to_river)
                
                equity_change = EquityChange(
                    player_id=player_data['player_id'],
                    flop_to_turn=flop_to_turn,
                    turn_to_river=turn_to_river,
                    flop_to_river=flop_to_river,
                    volatility=volatility
                )
                self.equity_changes.append(equity_change)
        
        return self.equity_changes
    
    
    def get_high_volatility_players(self, threshold: float = 0.3) -> List[EquityChange]:
        """Get players with high equity volatility."""
        if not self.equity_changes:
            self.calculate_equity_changes()
        
        return [ec for ec in self.equity_changes if ec.volatility > threshold]
    
    def get_equity_statistics(self) -> Dict[str, float]:
        """Calculate overall equity change statistics."""
        if not self.equity_changes:
            self.calculate_equity_changes()
        
        if not self.equity_changes:
            return {}
        
        flop_to_turn_changes = [ec.flop_to_turn for ec in self.equity_changes]
        turn_to_river_changes = [ec.turn_to_river for ec in self.equity_changes]
        volatilities = [ec.volatility for ec in self.equity_changes]
        
        return {
            'avg_flop_to_turn_change': statistics.mean(flop_to_turn_changes),
            'avg_turn_to_river_change': statistics.mean(turn_to_river_changes),
            'avg_volatility': statistics.mean(volatilities),
            'max_volatility': max(volatilities),
            'min_volatility': min(volatilities)
        }


class HandEvolutionTracker:
    """Tracks hand type evolution across streets."""
    
    def __init__(self, games: List[GameData], raw_data: Dict[str, Any]):
        """Initialize with parsed game data and raw data."""
        self.games = games
        self.raw_data = raw_data
        self.hand_progressions: List[HandProgression] = []
    
    def analyze_hand_progressions(self) -> List[HandProgression]:
        """Analyze how hands evolve from flop to river."""
        self.hand_progressions = []
        
        for game_raw in self.raw_data.get('games', []):
            for player_data in game_raw.get('player_hands', []):
                flop_hand = player_data.get('flop', {}).get('hand_type', '')
                turn_hand = player_data.get('turn', {}).get('hand_type', '')
                river_hand = player_data.get('river', {}).get('hand_type', '')
                
                # Determine if hand improved or degraded
                hand_strength_order = [
                    'High Card', 'Pair', 'Two Pairs', 'Three of a Kind',
                    'Straight', 'Flush', 'Full House', 'Four of a Kind',
                    'Straight Flush', 'Royal Flush'
                ]
                
                try:
                    flop_strength = hand_strength_order.index(flop_hand)
                    river_strength = hand_strength_order.index(river_hand)
                    
                    improved = river_strength > flop_strength
                    degraded = river_strength < flop_strength
                except ValueError:
                    improved = False
                    degraded = False
                
                progression = HandProgression(
                    player_id=player_data['player_id'],
                    flop_hand=flop_hand,
                    turn_hand=turn_hand,
                    river_hand=river_hand,
                    improved=improved,
                    degraded=degraded
                )
                self.hand_progressions.append(progression)
        
        return self.hand_progressions
    
    
    def get_improvement_statistics(self) -> Dict[str, Any]:
        """Get statistics on hand improvements and degradations."""
        if not self.hand_progressions:
            self.analyze_hand_progressions()
        
        total_hands = len(self.hand_progressions)
        if total_hands == 0:
            return {}
        
        improved_count = sum(1 for hp in self.hand_progressions if hp.improved)
        degraded_count = sum(1 for hp in self.hand_progressions if hp.degraded)
        
        # Count transitions by initial hand type
        improvement_by_initial: Dict[str, int] = defaultdict(int)
        degradation_by_initial: Dict[str, int] = defaultdict(int)
        total_by_initial: Dict[str, int] = defaultdict(int)
        
        for hp in self.hand_progressions:
            total_by_initial[hp.flop_hand] += 1
            if hp.improved:
                improvement_by_initial[hp.flop_hand] += 1
            elif hp.degraded:
                degradation_by_initial[hp.flop_hand] += 1
        
        return {
            'total_hands': total_hands,
            'improved_hands': improved_count,
            'degraded_hands': degraded_count,
            'improvement_rate': improved_count / total_hands,
            'degradation_rate': degraded_count / total_hands,
            'stable_rate': (total_hands - improved_count - degraded_count) / total_hands,
            'improvement_by_hand_type': dict(improvement_by_initial),
            'degradation_by_hand_type': dict(degradation_by_initial),
            'total_by_hand_type': dict(total_by_initial)
        }
    
    def get_most_common_progressions(self, limit: int = 10) -> List[Tuple[str, int]]:
        """Get most common hand type progressions."""
        if not self.hand_progressions:
            self.analyze_hand_progressions()
        
        progressions = [f"{hp.flop_hand} -> {hp.river_hand}" 
                       for hp in self.hand_progressions]
        progression_counts = Counter(progressions)
        
        return progression_counts.most_common(limit)


class WinningPatternAnalyzer:
    """Analyzes winning patterns and leader persistence."""
    
    def __init__(self, games: List[GameData]):
        """Initialize with parsed game data."""
        self.games = games
    
    def analyze_winner_persistence(self) -> Dict[str, float]:
        """Analyze how often early street leaders maintain their lead."""
        flop_to_turn_persistence = 0
        turn_to_river_persistence = 0
        flop_to_river_persistence = 0
        
        total_games = len(self.games)
        
        for game in self.games:
            # Check flop to turn persistence
            if (game.winners_flop and game.winners_turn and 
                game.winners_flop[0] == game.winners_turn[0]):
                flop_to_turn_persistence += 1
            
            # Check turn to river persistence
            if (game.winners_turn and game.winners_river and 
                game.winners_turn[0] == game.winners_river[0]):
                turn_to_river_persistence += 1
            
            # Check flop to river persistence
            if (game.winners_flop and game.winners_river and 
                game.winners_flop[0] == game.winners_river[0]):
                flop_to_river_persistence += 1
        
        if total_games == 0:
            return {}
        
        return {
            'flop_to_turn_persistence': flop_to_turn_persistence / total_games,
            'turn_to_river_persistence': turn_to_river_persistence / total_games,
            'flop_to_river_persistence': flop_to_river_persistence / total_games
        }
    
    def analyze_winning_hand_types(self) -> Dict[str, Dict[str, int]]:
        """Analyze distribution of winning hand types by street."""
        winning_hands: Dict[str, Counter[str]] = {
            'flop': Counter(),
            'turn': Counter(),
            'river': Counter()
        }
        
        for game in self.games:
            winning_hands['flop'][game.winning_hand_flop['hand_type']] += 1
            winning_hands['turn'][game.winning_hand_turn['hand_type']] += 1
            winning_hands['river'][game.winning_hand_river['hand_type']] += 1
        
        return {
            street: dict(counter.most_common()) 
            for street, counter in winning_hands.items()
        }


def analyze_poker_data(directory_path: str, pattern: str = "*.json", verbose: bool = False) -> Dict[str, Any]:
    """Main analysis function that runs all analyses on poker data from directory."""
    # Load and parse data
    loader = GameDataLoader(directory_path, pattern)
    if not loader.load_data(verbose):
        return {"error": "Failed to load data"}
    
    games = loader.parse_games()
    if not games:
        return {"error": "No games found in data"}
    
    # Run analyses
    if not loader.combined_raw_data:
        return {"error": "Failed to load raw data"}
    
    equity_analyzer = EquityAnalyzer(games, loader.combined_raw_data)
    hand_tracker = HandEvolutionTracker(games, loader.combined_raw_data)
    pattern_analyzer = WinningPatternAnalyzer(games)
    
    results = {
        'metadata': loader.get_metadata(),
        'total_games': len(games),
        'equity_statistics': equity_analyzer.get_equity_statistics(),
        'hand_progression_stats': hand_tracker.get_improvement_statistics(),
        'most_common_progressions': hand_tracker.get_most_common_progressions(),
        'winner_persistence': pattern_analyzer.analyze_winner_persistence(),
        'winning_hand_distribution': pattern_analyzer.analyze_winning_hand_types()
    }
    
    return results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze poker game data from JSON files')
    parser.add_argument('directory', help='Directory containing JSON game files')
    parser.add_argument('--pattern', default='*.json', 
                       help='File pattern to match (default: *.json)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Show detailed processing information')
    
    args = parser.parse_args()
    
    if not Path(args.directory).exists():
        print(f"Error: Directory '{args.directory}' does not exist")
        sys.exit(1)
    
    results = analyze_poker_data(args.directory, args.pattern, args.verbose)
    
    if "error" in results:
        print(f"Error: {results['error']}")
        sys.exit(1)
    
    # Print formatted results
    print("=== POKER DATA ANALYSIS RESULTS ===\n")
    
    metadata = results['metadata']
    print(f"Game Type: {metadata.get('game_type', 'Unknown')}")
    print(f"Players per Game: {metadata.get('num_of_players', 'Unknown')}")
    print(f"Files Processed: {metadata.get('total_files_processed', 0)}")
    if metadata.get('total_files_failed', 0) > 0:
        print(f"Files Failed: {metadata.get('total_files_failed', 0)}")
    print(f"Total Games Analyzed: {results['total_games']}\n")
    
    print("=== EQUITY ANALYSIS ===")
    equity_stats = results['equity_statistics']
    for key, value in equity_stats.items():
        print(f"{key.replace('_', ' ').title()}: {value:.4f}")
    
    print("\n=== HAND PROGRESSION ANALYSIS ===")
    progression_stats = results['hand_progression_stats']
    print(f"Improvement Rate: {progression_stats.get('improvement_rate', 0):.2%}")
    print(f"Degradation Rate: {progression_stats.get('degradation_rate', 0):.2%}")
    print(f"Stable Rate: {progression_stats.get('stable_rate', 0):.2%}")
    
    print("\n=== MOST COMMON PROGRESSIONS ===")
    for progression, count in results['most_common_progressions'][:5]:
        print(f"{progression}: {count}")
    
    print("\n=== WINNER PERSISTENCE ===")
    persistence = results['winner_persistence']
    for key, value in persistence.items():
        print(f"{key.replace('_', ' ').title()}: {value:.2%}")
    
    print("\n=== WINNING HAND DISTRIBUTION (RIVER) ===")
    river_winners = results['winning_hand_distribution'].get('river', {})
    for hand_type, count in list(river_winners.items())[:5]:
        print(f"{hand_type}: {count}")