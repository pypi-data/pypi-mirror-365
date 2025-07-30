"""Game Result Evaluation Module

This module provides functionality to evaluate poker games and determine
winners for each board and pot combination. It creates a game instance
from provided parameters and uses the built-in evaluation system.
"""

from typing import List, Dict, Any, Union
from collections import deque
from cardspy.card import ALL_CARDS, cards_mask
from pokermgr.table import Table
from pokermgr.player import TablePlayer
from pokermgr.pot import Pot
from pokermgr.board import Board
from pokermgr.game_base import Game
from pokermgr.game_texas_holdem_regular import GameTexasHoldemRegular
from pokermgr.game_plo_regular import GamePLORegular


def _get_card_mask_from_codes(card_codes: List[str]) -> int:
    """Convert list of card codes to bitmask format.
    
    Args:
        card_codes: List of card codes, supports both formats:
                   - 3-character with 'C' prefix: ['CAH', 'CKD']  
                   - 2-character standard: ['AH', 'KD']
        
    Returns:
        Integer bitmask representing the cards
        
    Raises:
        ValueError: If any card code is invalid or not found
    """
    cards = []
    for code in card_codes:
        # Convert 3-character to 2-character format if needed
        if len(code) == 3 and code.startswith('C'):
            normalized_code = code[1:]  # Remove 'C' prefix
        elif len(code) == 2:
            normalized_code = code
        else:
            raise ValueError(f"Invalid card code format: {code}. Expected 'CAH' or 'AH' format.")
        
        # Find the card object with matching code
        card_found = False
        for card in ALL_CARDS:
            if card.code == normalized_code:
                cards.append(card)
                card_found = True
                break
        
        if not card_found:
            raise ValueError(f'Card code {normalized_code} not found in available cards')
    
    return cards_mask(cards)


def evaluate_game(
    player_cards: Dict[str, List[str]],
    board_cards: List[List[str]],
    pots: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Evaluate a poker game and determine winners for each board and pot.
    
    This function creates a game instance from the provided parameters and
    uses the game's built-in evaluation system to determine winners.
    
    Args:
        player_cards: Dictionary mapping player names to their hole cards
            Example: {"P1": ["CAH", "CAD"], "P2": ["CKH", "CKD"]}
        board_cards: List of lists, where each inner list contains 5 board cards
            Example: [["C7H", "C5S", "CTD", "C7C", "CKH"]]
        pots: List of pot dictionaries with 'amount' and 'participants' keys
            Example: [{"amount": 100, "participants": ["P1", "P2"]}]
    
    Returns:
        List of dictionaries with game results. Each dictionary contains:
        - "pot": Pot key/identifier
        - "board": Board key/identifier  
        - "share_per_player": Amount each winner receives
        - "winners": List of winner strings with format "{player} - {cards} - {hand_type}"
    
    Raises:
        ValueError: If player cards are inconsistent, invalid board cards, or empty pots
        KeyError: If pot participants reference non-existent players
    """
    # Validation
    if not player_cards:
        raise ValueError("Player cards cannot be empty")
    
    if not board_cards:
        raise ValueError("Board cards cannot be empty")
    
    if not pots:
        raise ValueError("Pots cannot be empty")
    
    # Validate all players have same number of cards
    cards_per_player = [len(cards) for cards in player_cards.values()]
    if not all(count == cards_per_player[0] for count in cards_per_player):
        raise ValueError("All players must have the same number of hole cards")
    
    hand_size = cards_per_player[0]
    if hand_size not in [2, 4, 5, 6, 7]:
        raise ValueError(f"Invalid hand size {hand_size}. Must be 2 (Hold'em) or 4-7 (Omaha)")
    
    # Validate board cards
    for board_idx, board_card_list in enumerate(board_cards):
        if len(board_card_list) != 5:
            raise ValueError(f"Board {board_idx} must have exactly 5 cards, got {len(board_card_list)}")
    
    # Validate pot participants
    all_players = set(player_cards.keys())
    for pot_idx, pot_info in enumerate(pots):
        if 'participants' not in pot_info:
            raise ValueError(f"Pot {pot_idx} missing 'participants' key")
        if 'amount' not in pot_info:
            raise ValueError(f"Pot {pot_idx} missing 'amount' key")
        
        pot_participant_names = set(pot_info['participants'])
        if not pot_participant_names.issubset(all_players):
            invalid_players = pot_participant_names - all_players
            raise KeyError(f"Pot {pot_idx} references non-existent players: {invalid_players}")
    
    # Create players
    players_list = []
    for player_name, cards in player_cards.items():
        player = TablePlayer(player_name)
        # Set a large stack to avoid all-in constraints during evaluation
        player.stack = 10000.0
        # Convert card codes to bitmask and set hole cards
        card_mask = _get_card_mask_from_codes(cards)
        player.set_hole_cards(card_mask)
        players_list.append(player)
    
    # Create table
    table = Table("eval_table", deque(players_list))
    
    # Determine game type and create appropriate game instance
    game: Game
    if hand_size == 2:
        # Texas Hold'em
        game = GameTexasHoldemRegular(
            key=1,
            table=table,
            small_blind=0,  # No blinds needed for evaluation
            big_blind=0,
            initial_board_count=len(board_cards)
        )
    else:
        # Omaha (4-7 cards)
        game = GamePLORegular(
            key=1,
            table=table,
            small_blind=0,  # No blinds needed for evaluation
            big_blind=0,
            initial_board_count=len(board_cards),
            hand_size=hand_size
        )
    
    # Clear existing pots and create new ones based on input
    game.pots = []
    for pot_index, pot_data in enumerate(pots):
        # Find player objects for participants
        eligible_players: List[TablePlayer] = []
        for participant_name in pot_data['participants']:
            player_obj = next(p for p in players_list if p.code == participant_name)
            eligible_players.append(player_obj)
        
        # Create pot
        new_pot = Pot(key=pot_index, stack=float(pot_data['amount']), players=eligible_players)
        game.pots.append(new_pot)
    
    # Set board cards
    for board_index, board_card_list in enumerate(board_cards):
        current_board: Board
        if board_index < len(game.boards):
            current_board = game.boards[board_index]
        else:
            # Add additional boards if needed
            current_board = Board(key=board_index)
            game.boards.append(current_board)
        
        # Convert board cards to bitmask
        board_mask = _get_card_mask_from_codes(board_card_list)
        current_board.cards = board_mask
    
    # Use the game's built-in evaluation system
    return game.get_result()


def format_result_summary(result: List[Dict[str, Any]]) -> str:
    """Format game result into a human-readable summary.
    
    Args:
        result: Result from evaluate_game function
        
    Returns:
        Formatted string summary of the game result
    """
    if not result:
        return "No results to display"
    
    summary_lines = []
    summary_lines.append("Game Evaluation Results:")
    summary_lines.append("=" * 50)
    
    # Group results by pot
    pots_data: Dict[Any, List[Dict[str, Any]]] = {}
    for entry in result:
        pot_key = entry['pot']
        if pot_key not in pots_data:
            pots_data[pot_key] = []
        pots_data[pot_key].append(entry)
    
    for pot_key, pot_results in pots_data.items():
        summary_lines.append(f"\nPot {pot_key}:")
        summary_lines.append("-" * 20)
        
        for board_result in pot_results:
            board_key = board_result['board']
            share = board_result['share_per_player']
            winners = board_result['winners']
            
            summary_lines.append(f"  Board {board_key}:")
            if winners:
                summary_lines.append(f"    Share per winner: ${share:.2f}")
                for winner in winners:
                    summary_lines.append(f"    Winner: {winner}")
            else:
                summary_lines.append(f"    No winners")
    
    return "\n".join(summary_lines)