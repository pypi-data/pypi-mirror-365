"""Poker Hand Evaluation Module

This module provides functionality to evaluate poker hands and determine the winner(s)
among multiple players. It handles the core logic for comparing hand strengths
based on standard poker hand rankings.

Functions:
    get_winners: Determines the winning player(s) based on their best 5-card hand
                evaluated against the community cards.
"""
from itertools import combinations
from typing import List, Tuple
from cardspy.card import extract_cards, cards_mask
from cardspy.deck import Deck
from pokermgr.player import TablePlayer, BoardPlayer
from pokermgr.funcs import get_hand_type_weight
from pokermgr.hand import Hand


def evaluate(
    board_cards_keys: List[int],
    players: List[TablePlayer],
    use_exhaustive_equity: bool = True
) -> List[TablePlayer]:
    """
    Evaluate poker hands and set hand/equity values for all players across multiple boards.

    Args:
        board_cards_keys: List of integer bitmasks representing the community cards for each board.
        players: List of TablePlayer instances representing the players in the hand.
        use_exhaustive_equity: If True and exactly 3 board cards are present on all boards, 
                              uses exhaustive equity calculation. Otherwise uses 
                              simple ranking-based equity.

    Returns:
        A list of TablePlayer instances with updated hand and equity values.
    """
    if not board_cards_keys or not players:
        return players

    # Convert to board players for hand evaluation
    board_players = [player.to_board_player() for player in players]
    
    # Calculate best hand for each player across all boards
    for board_player in board_players:
        best_hand = get_player_best_hand(board_player, board_cards_keys)
        board_player.hand = best_hand

    # Calculate equity for each player across all boards
    if use_exhaustive_equity and all(board_key.bit_count() == 3 for board_key in board_cards_keys):
        # Use exhaustive equity calculation for flop scenarios
        calculate_exhaustive_equity(board_players, board_cards_keys)
    else:
        # Use simple equity calculation based on hand strength across boards
        _calculate_multi_board_simple_equity(board_players, board_cards_keys)
    
    # Update the original TablePlayer objects with equity values
    for i, player in enumerate(players):
        player.equity = board_players[i].equity

    return players


def get_winners(
    board_cards_key: int,
    players: List[TablePlayer]
) -> List[BoardPlayer]:
    """
    Determine the winning player(s) based on their best 5-card hand 
    evaluated against the community cards.

    Args:
        board_cards_key: Integer bitmask representing the community cards.
        players: List of TablePlayer instances representing the players in the hand.

    Returns:
        A list of BoardPlayer instances representing the winning players,
        with their hand attribute set to their best 5-card hand.
    """
    if board_cards_key == 0 or not players:
        return []
        
    # Convert to board players for hand evaluation
    board_players = [player.to_board_player() for player in players]
    
    # Calculate best hand for each player on this board
    for board_player in board_players:
        best_hand = get_player_best_hand(board_player, [board_cards_key])
        board_player.hand = best_hand

    # Find winners for this board
    board_winners = _determine_winners_from_hands(board_players)
    
    return board_winners


def get_winners_multi_board(
    board_cards_keys: List[int],
    players: List[TablePlayer]
) -> List[List[BoardPlayer]]:
    """
    Determine the winning player(s) for each board based on their best 5-card hand 
    evaluated against the community cards.

    Args:
        board_cards_keys: List of integer bitmasks representing the community cards for each board.
        players: List of TablePlayer instances representing the players in the hand.

    Returns:
        A list of lists, where each inner list contains the BoardPlayer instances 
        representing the winning players for that specific board.
    """
    if not board_cards_keys:
        return []
    
    winners_per_board = []
    
    # Determine winners for each board individually
    for board_cards_key in board_cards_keys:
        board_winners = get_winners(board_cards_key, players)
        winners_per_board.append(board_winners)
    
    return winners_per_board


def _get_player_best_weight(player: TablePlayer, board_cards_key: int) -> int:
    """Calculate the best possible hand weight for a player."""
    player_cards_count = player.hole_cards.key.bit_count()

    if player_cards_count == 2:
        return _get_holdem_best_weight(player, board_cards_key)
    elif player_cards_count >= 4:
        return _get_omaha_best_weight(player, board_cards_key)

    return 0


def get_player_best_hand(player: BoardPlayer, board_cards_keys: List[int]) -> Hand:
    """Calculate the best possible hand for a player across all boards."""
    player_cards_count = player.hole_cards.key.bit_count()

    if player_cards_count < 2:
        raise ValueError("Player must have at least 2 hole cards")
    
    best_hand = Hand(0)
    
    # Find the best hand across all boards
    for board_cards_key in board_cards_keys:
        if board_cards_key == 0:
            continue
            
        if player_cards_count == 2:
            current_hand = _get_holdem_best_hand(player, board_cards_key)
        elif player_cards_count >= 4:
            current_hand = _get_omaha_best_hand(player, board_cards_key)
        else:
            continue
            
        # Keep the best hand found across all boards
        if current_hand.weight > best_hand.weight:
            best_hand = current_hand

    return best_hand


def _get_holdem_best_weight(player: TablePlayer, board_cards_key: int) -> int:
    """Calculate best weight for Hold'em game (2 hole cards)."""
    all_cards_key = player.hole_cards.key | board_cards_key
    all_cards = extract_cards(all_cards_key)

    best_weight = 0
    for combo in combinations(all_cards, 5):
        combo_key = cards_mask(list(combo))
        weight, _, _ = get_hand_type_weight(combo_key)
        best_weight = max(best_weight, weight)

    return best_weight


def _get_holdem_best_hand(player: BoardPlayer, board_cards_key: int) -> Hand:
    """Calculate best weight for Hold'em game (2 hole cards)."""
    all_cards_key = player.hole_cards.key | board_cards_key
    all_cards = extract_cards(all_cards_key)

    best_hand = Hand(0)
    for combo in combinations(all_cards, 5):
        combo_key = cards_mask(list(combo))
        weight, type_key, type_name = get_hand_type_weight(combo_key)
        if weight > best_hand.weight:
            best_hand = Hand(combo_key)
            best_hand.type_key = type_key
            best_hand.type_name = type_name
            best_hand.weight = weight

    return best_hand


def _get_omaha_best_weight(player: TablePlayer, board_cards_key: int) -> int:
    """Calculate best weight for Omaha game (4+ hole cards)."""
    player_cards = extract_cards(player.hole_cards.key)
    board_cards = extract_cards(board_cards_key)

    best_weight = 0
    for player_cards_combo in combinations(player_cards, 2):
        for board_cards_combo in combinations(board_cards, 3):
            combo = player_cards_combo + board_cards_combo
            combo_key = cards_mask(list(combo))
            weight, _, _ = get_hand_type_weight(combo_key)
            best_weight = max(best_weight, weight)

    return best_weight


def _get_omaha_best_hand(player: BoardPlayer, board_cards_key: int) -> Hand:
    """Calculate best weight for Omaha game (4+ hole cards)."""
    player_cards = extract_cards(player.hole_cards.key)
    board_cards = extract_cards(board_cards_key)

    best_hand = Hand(0)
    for player_cards_combo in combinations(player_cards, 2):
        for board_cards_combo in combinations(board_cards, 3):
            combo = player_cards_combo + board_cards_combo
            combo_key = cards_mask(list(combo))
            weight, type_key, type_name = get_hand_type_weight(combo_key)
            if weight > best_hand.weight:
                best_hand = Hand(combo_key)
                best_hand.type_key = type_key
                best_hand.type_name = type_name
                best_hand.weight = weight

    return best_hand


def _determine_winners_from_weights(
    player_weights: List[Tuple[TablePlayer, int]]
) -> List[TablePlayer]:
    """Determine winners from list of (player, weight) tuples."""
    if not player_weights:
        return []

    # Find the maximum weight
    max_weight = max(weight for _, weight in player_weights)

    # Return all players with the maximum weight
    return [player for player, weight in player_weights if weight == max_weight]


def calculate_exhaustive_equity(players: List[BoardPlayer], board_cards_keys: List[int]) -> None:
    """
    Calculate equity for each player after flop by exhaustively checking all
    possible turn and river card combinations across multiple boards.
    
    This function assumes the flop (3 cards) has already been dealt on all boards and calculates
    the combined win probability for each player across all possible turn/river combinations
    on all boards simultaneously.
    
    Args:
        players: List of BoardPlayer instances representing the players in the hand.
        board_cards_keys: List of integer bitmasks representing the flop cards (3 cards each).
        
    Note:
        - Assumes exactly 3 board cards (flop) have been dealt on each board
        - Updates each player's equity attribute in-place
        - Uses exhaustive enumeration across all boards simultaneously
        - Handles both Hold'em and Omaha based on hole card count
    """
    if not players or not board_cards_keys:
        return
        
    for board_cards_key in board_cards_keys:
        if board_cards_key.bit_count() != 3:
            raise ValueError("Expected exactly 3 board cards (flop) on each board")
    
    # Initialize equity counters for each player
    player_wins = {player.code: 0 for player in players}
    player_ties = {player.code: 0 for player in players}
    
    # Create deck and remove known cards
    deck = Deck()
    
    # Remove all flop cards from all boards from deck
    all_flop_cards = set()
    for board_cards_key in board_cards_keys:
        flop_cards = extract_cards(board_cards_key)
        for card in flop_cards:
            all_flop_cards.add(card.key)
    
    for card_key in all_flop_cards:
        deck.deal_specific_card(card_key)
    
    # Remove each player's hole cards from deck
    for player in players:
        hole_cards = extract_cards(player.hole_cards.key)
        for card in hole_cards:
            deck.deal_specific_card(card.key)
    
    # Get remaining cards for turn and river
    remaining_cards = deck.get_remaining_cards()
    
    # Number of turn/river cards needed (2 per board)
    cards_needed = len(board_cards_keys) * 2
    
    # Exhaustively check all turn/river combinations across all boards
    total_combinations = 0
    
    for turn_river_combo in combinations(remaining_cards, cards_needed):
        total_combinations += 1
        
        # Create complete boards (flop + turn + river for each board)
        complete_board_keys = []
        for i, board_cards_key in enumerate(board_cards_keys):
            turn_card = turn_river_combo[i * 2]
            river_card = turn_river_combo[i * 2 + 1]
            complete_board_key = board_cards_key | turn_card.key | river_card.key
            complete_board_keys.append(complete_board_key)
        
        # Calculate how many boards each player wins
        board_wins_per_player = {player.code: 0 for player in players}
        board_ties_per_player = {player.code: 0 for player in players}
        
        for complete_board_key in complete_board_keys:
            # Evaluate best hand for each player on this board
            for player in players:
                player.hand = get_player_best_hand(player, [complete_board_key])
            
            # Determine winners for this board
            winners = _determine_winners_from_hands(players)
            
            # Update board win/tie counts
            if len(winners) == 1:
                board_wins_per_player[winners[0].code] += 1
            else:
                for winner in winners:
                    board_ties_per_player[winner.code] += 1 / len(winners)
        
        # Update overall win counts based on combined board performance
        # Player with most boards won gets the win, ties if equal
        max_boards = max(board_wins_per_player[p.code] + board_ties_per_player[p.code] for p in players)
        top_players = [p for p in players if board_wins_per_player[p.code] + board_ties_per_player[p.code] == max_boards]
        
        if len(top_players) == 1:
            player_wins[top_players[0].code] += 1
        else:
            for player in top_players:
                player_ties[player.code] += 1
    
    # Calculate final equity for each player
    for player in players:
        wins = player_wins[player.code]
        ties = player_ties[player.code]
        
        # Calculate equity: (wins + ties/num_tied_players) / total_combinations
        num_players = len(players)
        equity = (wins + ties / num_players) / total_combinations if total_combinations > 0 else 0.0
        player.equity = equity


def _calculate_multi_board_simple_equity(board_players: List[BoardPlayer], board_cards_keys: List[int]) -> None:
    """Calculate equity for each player based on combined performance across multiple boards."""
    if not board_players or not board_cards_keys:
        return
    
    # Initialize counters for each player
    player_board_wins = {player.code: 0.0 for player in board_players}
    
    # Calculate wins per board for each player
    for board_cards_key in board_cards_keys:
        if board_cards_key == 0:
            continue
            
        # Evaluate each player's hand on this specific board
        board_hands = {}
        for player in board_players:
            if player.hole_cards.key.bit_count() == 2:
                hand = _get_holdem_best_hand(player, board_cards_key)
            elif player.hole_cards.key.bit_count() >= 4:
                hand = _get_omaha_best_hand(player, board_cards_key)
            else:
                hand = Hand(0)
            board_hands[player.code] = hand
        
        # Find the best weight on this board
        if not board_hands:
            continue
            
        best_weight = max(hand.weight for hand in board_hands.values())
        
        # Find all players with the best weight (winners/tied players)
        board_winners = [player for player in board_players if board_hands[player.code].weight == best_weight]
        
        # Each winner gets 1/num_winners of this board
        win_share = 1.0 / len(board_winners) if board_winners else 0.0
        for winner in board_winners:
            player_board_wins[winner.code] += win_share
    
    # Calculate final equity: total boards won / total boards
    total_boards = len([key for key in board_cards_keys if key != 0])
    
    for player in board_players:
        if total_boards > 0:
            player.equity = player_board_wins[player.code] / total_boards
        else:
            player.equity = 0.0


def _calculate_simple_equity(board_players: List[BoardPlayer]) -> None:
    """Calculate equity for each player based on their hand strength (single board legacy)."""
    if not board_players:
        return
    
    # Group players by hand strength
    weight_groups = {}
    for player in board_players:
        weight = player.hand.weight
        if weight not in weight_groups:
            weight_groups[weight] = []
        weight_groups[weight].append(player)
    
    # Sort weights in descending order (best hands first)
    sorted_weights = sorted(weight_groups.keys(), reverse=True)
    
    # Calculate equity based on hand strength ranking
    total_players = len(board_players)
    
    for i, weight in enumerate(sorted_weights):
        players_with_weight = weight_groups[weight]
        
        # Players with better hands (lower index)
        better_players = sum(len(weight_groups[w]) for w in sorted_weights[:i])
        
        # Players with equal hands
        equal_players = len(players_with_weight)
        
        # Players with worse hands
        worse_players = total_players - better_players - equal_players
        
        # Equity calculation: 
        # - Win against all worse players: worse_players / total_players  
        # - Tie with equal players: (equal_players / total_players) / equal_players = 1 / total_players
        # - Lose against better players: 0
        equity = (worse_players + equal_players) / total_players / equal_players
        
        # Set equity for all players with this hand strength
        for player in players_with_weight:
            player.equity = equity


def _determine_winners_from_hands(
    players: List[BoardPlayer]
) -> List[BoardPlayer]:
    """Determine winners from list of (player, weight) tuples."""
    if not players:
        return []

    winners: List[BoardPlayer] = []

    # Find the maximum weight
    best_weight = 0
    for player in players:
        if player.hand.weight > best_weight:
            best_weight = player.hand.weight
            winners = [player]
        elif player.hand.weight == best_weight:
            winners.append(player)

    return winners
