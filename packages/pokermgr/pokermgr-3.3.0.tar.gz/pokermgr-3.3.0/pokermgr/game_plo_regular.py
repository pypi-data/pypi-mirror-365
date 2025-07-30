"""Pot Limit Omaha Regular Game

This module implements the Pot Limit Omaha Regular game with small and big blinds.
Supports 4, 5, 6, and 7-card Omaha variants with pot-limit betting structure.
"""

from typing import Dict, List, Set, Tuple, Optional
from itertools import combinations
from cardspy.card import extract_cards

from pokermgr.table import Table
from pokermgr.action import PlayerAction, PlayerActionType
from pokermgr.game_plo import GamePLO
from pokermgr.player import TablePlayer, PlayerStatus
from pokermgr.game_street import GameStreet


class GamePLORegular(GamePLO):
    """Pot Limit Omaha Regular game with small and big blinds.

    This class implements a Pot Limit Omaha game where players post
    small and big blinds, and betting follows pot-limit rules.
    Supports 4, 5, 6, and 7-card Omaha variants.

    Args:
        key: Unique identifier for the game
        table: Table object containing player information
        small_blind: Size of the small blind
        big_blind: Size of the big blind
        initial_board_count: Number of boards to use (default: 1)
        hand_size: Number of hole cards (4, 5, 6, or 7)
        betting_structure: Betting structure (always "pot_limit" for PLO)
        game_type: Game type (always "omaha" for PLO)

    Attributes:
        small_blind: Size of the small blind
        big_blind: Size of the big blind
        hand_size: Number of hole cards per player
        betting_structure: The betting structure ("pot_limit")
        game_type: The game type ("omaha")
        player_contributions: Dict tracking player contributions this round
    """

    def __init__(
        self,
        key: int,
        table: Table,
        small_blind: int,
        big_blind: int,
        initial_board_count: int = 1,
        hand_size: int = 4,
        betting_structure: str = "pot_limit",
        game_type: str = "omaha",
    ) -> None:
        """Initialize PLO Regular game.
        
        Args:
            key: Unique identifier for the game
            table: Table object containing player information
            small_blind: Size of the small blind
            big_blind: Size of the big blind
            initial_board_count: Number of boards to use (default: 1)
            hand_size: Number of hole cards (4, 5, 6, or 7)
            betting_structure: Betting structure (default: "pot_limit")
            game_type: Game type (default: "omaha")
        
        Raises:
            ValueError: If hand_size is not between 4 and 7 inclusive
        """
        super().__init__(key, table, initial_board_count, hand_size, betting_structure, game_type)
        self.small_blind = small_blind
        self.big_blind = big_blind
        
        # Set initial player to act to first player after big blind (position 2)
        if len(self.table.players) > 2:
            self.player_to_act = self.table.players[2]
        elif len(self.table.players) == 2:
            self.player_to_act = self.table.players[0]  # Heads up: SB acts first preflop


    def deal_hole_cards(self) -> None:
        """Deal hole cards to each player.
        
        Deals the specified number of hole cards (hand_size) to each player.
        
        Raises:
            ValueError: If there are not enough cards in the deck
        """
        total_cards_needed = len(self.table.players) * self.hand_size
        if total_cards_needed > 52:
            raise ValueError(f"Not enough cards in deck. Need {total_cards_needed}, deck has 52.")
        
        for player in self.table.players:
            hole_cards = self.deck.deal_cards(self.hand_size)
            
            # Add player to each board
            for board in self.boards:
                board.add_board_player(player, hole_cards)

    def post_blinds(self) -> None:
        """Post small and big blinds."""
        if len(self.table.players) < 2:
            return

        # In a real implementation, we'd have positions for small blind and big blind
        # For simplicity, assume first two players are SB and BB
        sb_player = self.table.players[0] if len(self.table.players) > 0 else None
        bb_player = self.table.players[1] if len(self.table.players) > 1 else None

        # Create pot if it doesn't exist
        if not self.pots:
            self.add_pot(0)

        blinds_posted = {}
        
        # Post small blind
        if sb_player:
            self.player_contributions[sb_player] = self.small_blind
            self.pots[0].stack += self.small_blind
            sb_player.stack -= self.small_blind
            self.pot_current_street += self.small_blind  # Track for pot limit calculations
            blinds_posted['small_blind'] = {
                'player': getattr(sb_player, 'code', str(sb_player)),
                'amount': self.small_blind
            }

        # Post big blind (this creates the "bet" that others must call)
        if bb_player:
            self.player_contributions[bb_player] = self.big_blind
            self.pots[0].stack += self.big_blind
            bb_player.stack -= self.big_blind
            self.current_bet = self.big_blind  # Set current bet
            self.pot_current_street += self.big_blind  # Track for pot limit calculations
            blinds_posted['big_blind'] = {
                'player': getattr(bb_player, 'code', str(bb_player)),
                'amount': self.big_blind
            }
            
        # Blind posting tracked only via external process_game_action

    def get_minimum_bet_amount(self) -> float:
        """Get the minimum bet amount.

        Returns:
            float: Minimum bet amount (big blind)
        """
        return self.big_blind

    def _is_valid_action(self, action: PlayerAction) -> bool:
        """Validate if the given action is allowed in PLO Regular.

        Args:
            action: The action to validate

        Returns:
            bool: True if the action is valid, False otherwise
        """
        # Check basic player status
        if action.player.status in [PlayerStatus.FOLDED, PlayerStatus.SITOUT, PlayerStatus.ALLIN]:
            return False
        
        # Check sufficient stack
        if action.player.stack < action.stack:
            return False

        # Validate specific action types
        if action.action_type == PlayerActionType.FOLD:
            return True
            
        elif action.action_type == PlayerActionType.CHECK:
            # Can only check if no bet to call
            return self.current_bet == 0
            
        elif action.action_type == PlayerActionType.CALL:
            # Call amount should match what's needed to call
            call_amount = self.calculate_call_amount(action.player)
            return action.stack == call_amount
            
        elif action.action_type == PlayerActionType.BET:
            # Validate pot-limit bet
            return self._validate_pot_limit_bet(action)
            
        elif action.action_type == PlayerActionType.RAISE:
            # Validate pot-limit raise
            return self._validate_pot_limit_raise(action)
            
        elif action.action_type == PlayerActionType.ALLIN:
            return True

        return False





    def register_action(self, action: PlayerAction) -> bool:
        """Register an action and update game state.

        Args:
            action: PlayerAction to register

        Returns:
            bool: True if action was registered successfully
        """
        # Use the base class register_action method which handles undo state snapshots
        return super().register_action(action)

    def advance_to_flop(self, burn_card: bool = False) -> None:
        """Advance the game to the flop and deal 3 community cards.
        
        Args:
            burn_card: If True, burn a card before dealing flop
        """
        self.game_street = GameStreet.FLOP
        
        # Burn a card if requested
        if burn_card:
            self.deck.deal_cards(1)
        
        # Deal 3 community cards to each board
        for board in self.boards:
            flop_cards = self.deck.deal_cards(3)
            board.add_cards(flop_cards)
        
        # Advance street for PLO pot tracking
        self._advance_street()
        
        # Board dealing tracked only via external process_game_action

    def advance_to_turn(self, burn_card: bool = False) -> None:
        """Advance the game to the turn and deal 1 community card.
        
        Args:
            burn_card: If True, burn a card before dealing turn
        """
        self.game_street = GameStreet.TURN
        
        # Burn a card if requested
        if burn_card:
            self.deck.deal_cards(1)
        
        # Deal 1 community card to each board
        for board in self.boards:
            turn_card = self.deck.deal_cards(1)
            board.add_cards(turn_card)
        
        # Advance street for PLO pot tracking
        self._advance_street()
        
        # Board dealing tracked only via external process_game_action

    def advance_to_river(self, burn_card: bool = False) -> None:
        """Advance the game to the river and deal 1 community card.
        
        Args:
            burn_card: If True, burn a card before dealing river
        """
        self.game_street = GameStreet.RIVER
        
        # Burn a card if requested
        if burn_card:
            self.deck.deal_cards(1)
        
        # Deal 1 community card to each board
        for board in self.boards:
            river_card = self.deck.deal_cards(1)
            board.add_cards(river_card)
        
        # Advance street for PLO pot tracking
        self._advance_street()
        
        # Board dealing tracked only via external process_game_action

    def advance_to_showdown(self) -> None:
        """Advance the game to showdown."""
        self.game_street = GameStreet.SHOWDOWN

    def is_hand_complete(self) -> bool:
        """Check if the hand is complete.
        
        Returns:
            bool: True if only one player remains active or showdown is reached
        """
        active_players = [p for p in self.table.players if p.status not in [PlayerStatus.FOLDED]]
        return len(active_players) <= 1 or self.game_street == GameStreet.SHOWDOWN

    def get_winners(self) -> List[TablePlayer]:
        """Get the winners of the hand.
        
        Returns:
            List of winning players
        """
        active_players = [p for p in self.table.players if p.status not in [PlayerStatus.FOLDED]]
        
        if len(active_players) == 1:
            return active_players
        
        # For now, return all active players (hand evaluation would be implemented here)
        return active_players

    def get_board_player(self, player: TablePlayer, board_index: int) -> Optional[object]:
        """Get the board player for a given table player and board.
        
        Args:
            player: The table player
            board_index: Index of the board
            
        Returns:
            Board player object or None if not found
        """
        if board_index >= len(self.boards):
            return None
            
        board = self.boards[board_index]
        for board_player in board.players:
            if board_player.code == player.code:
                return board_player
        
        return None

    def get_valid_hand_combinations(self, hole_cards: List[int], board_cards: List[int]) -> List[List[int]]:
        """Get all valid Omaha hand combinations using exactly 2 hole + 3 board cards.
        
        Args:
            hole_cards: List of hole card integers
            board_cards: List of board card integers
            
        Returns:
            List of valid 5-card combinations
        """
        valid_combinations = []
        
        # Generate all combinations of 2 hole cards
        for hole_combo in combinations(hole_cards, 2):
            # Generate all combinations of 3 board cards
            for board_combo in combinations(board_cards, 3):
                # Combine into 5-card hand
                hand = list(hole_combo) + list(board_combo)
                valid_combinations.append(hand)
        
        return valid_combinations

    def is_valid_omaha_hand(self, hand: List[int], hole_cards: List[int], board_cards: List[int]) -> bool:
        """Check if a hand is a valid Omaha hand (exactly 2 hole + 3 board cards).
        
        Args:
            hand: 5-card hand to validate
            hole_cards: Available hole cards
            board_cards: Available board cards
            
        Returns:
            bool: True if hand follows Omaha 2+3 rule
        """
        if len(hand) != 5:
            return False
            
        hole_used = sum(1 for card in hand if card in hole_cards)
        board_used = sum(1 for card in hand if card in board_cards)
        
        return hole_used == 2 and board_used == 3

    def get_best_omaha_hand(self, hole_cards: List[int], board_cards: List[int]) -> List[int]:
        """Get the best possible Omaha hand using 2 hole + 3 board cards.
        
        Args:
            hole_cards: Available hole cards
            board_cards: Available board cards
            
        Returns:
            Best 5-card Omaha hand
        """
        valid_combinations = self.get_valid_hand_combinations(hole_cards, board_cards)
        
        # For now, return the first valid combination
        # In a full implementation, this would evaluate hand strength
        if valid_combinations:
            return valid_combinations[0]
        
        return []