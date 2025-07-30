"""Base Pot Limit Omaha Game Class

This module implements the base PLO game class that provides PLO-specific
functionality including proper pot limit calculations using the industry
standard (3L + T) + S formula.
"""

from typing import Dict, List, Optional
from itertools import combinations
from cardspy.card import extract_cards

from pokermgr.table import Table
from pokermgr.action import PlayerAction, PlayerActionType
from pokermgr.game_base import Game
from pokermgr.player import TablePlayer, PlayerStatus
from pokermgr.game_street import GameStreet


class GamePLO(Game):
    """Base class for Pot Limit Omaha poker games.

    This class implements PLO-specific rules including proper pot limit
    calculations, Omaha hole card dealing, and hand validation. It serves
    as a base class for different PLO variants (regular, bomb pots).

    Uses the correct PLO pot limit formula: (3L + T) + S
    Where:
    - L = last wager (current bet)
    - T = trail (all bets in current street excluding last bet)
    - S = starting pot (pot from previous streets)

    Args:
        key: Unique identifier for the game
        table: Table object containing player information
        initial_board_count: Number of boards to use (default: 1)
        hand_size: Number of hole cards (4, 5, 6, or 7)
        betting_structure: Betting structure (always "pot_limit" for PLO)
        game_type: Game type (always "omaha" for PLO)

    Attributes:
        hand_size: Number of hole cards per player
        betting_structure: The betting structure ("pot_limit")
        game_type: The game type ("omaha")
        pot_previous_street: Pot amount from previous betting rounds
        pot_current_street: Pot amount from current betting round
        current_bet: Highest bet amount in current round
        player_contributions: Dict tracking player contributions this round
    """

    def __init__(
        self,
        key: int,
        table: Table,
        initial_board_count: int = 1,
        hand_size: int = 4,
        betting_structure: str = "pot_limit",
        game_type: str = "omaha",
    ) -> None:
        """Initialize PLO base game.
        
        Args:
            key: Unique identifier for the game
            table: Table object containing player information
            initial_board_count: Number of boards to use (default: 1)
            hand_size: Number of hole cards (4, 5, 6, or 7)
            betting_structure: Betting structure (default: "pot_limit")
            game_type: Game type (default: "omaha")
        
        Raises:
            ValueError: If hand_size is not between 4 and 7 inclusive
        """
        if hand_size not in [4, 5, 6, 7]:
            raise ValueError(f"Invalid hand size {hand_size}. Must be 4, 5, 6, or 7.")
        
        super().__init__(key, table, initial_board_count)
        self.hand_size = hand_size
        self.betting_structure = betting_structure
        self.game_type = game_type
        
        # PLO-specific pot tracking for correct pot limit calculations
        self.pot_previous_street: float = 0.0  # Pot from previous streets
        self.pot_current_street: float = 0.0   # Pot from current street
        self.current_bet: float = 0.0           # Highest bet in current round
        self.player_contributions: Dict[TablePlayer, float] = {}

    def _core_deal_hole_cards(self) -> None:
        """Deal hole cards to each player based on hand_size.
        
        This implements Omaha hole card dealing where each player
        receives hand_size (4, 5, 6, or 7) private cards.
        """
        for player in self.table.players:
            player.set_hole_cards(self.deck.deal_cards(self.hand_size))

    def calculate_max_pot_limit_bet(self) -> float:
        """Calculate maximum allowable pot limit bet using correct PLO formula.

        Uses the industry standard formula: (3L + T) + S
        Where:
        - L = last wager (current bet)
        - T = trail (all bets in current street excluding the last bet)
        - S = starting pot (pot from previous streets)

        Returns:
            float: Maximum bet amount allowed under pot limit rules
        """
        L = self.current_bet  # Last wager
        # Trail is total bet in current street excluding the last bet
        # If current_bet is 0, then trail is the entire pot_current_street
        T = max(0, self.pot_current_street - self.current_bet)  # Trail
        S = self.pot_previous_street  # Starting pot

        # Apply the formula: (3L + T) + S = M
        # This represents: 3 times the last bet + trail + starting pot
        max_bet = (3 * L + T) + S
        
        return max_bet

    def calculate_max_pot_limit_raise(self, player: TablePlayer) -> float:
        """Calculate maximum allowed raise for a player in pot-limit games.

        This uses the correct PLO formula to determine the maximum raise amount
        a player can make, limited by their stack size.

        Args:
            player: Player making the raise

        Returns:
            float: Maximum raise amount (total chips to put in)
        """
        # Calculate call amount first
        call_amount = self.calculate_call_amount(player)
        
        # Calculate pot size after the call would be made
        pot_after_call = self.pot_previous_street + self.pot_current_street + call_amount
        
        # Use PLO formula for maximum raise: call + pot_after_call
        max_raise_total = call_amount + pot_after_call
        
        # Limited by player's stack
        return min(max_raise_total, player.stack)

    def calculate_call_amount(self, player: TablePlayer) -> float:
        """Calculate the amount a player needs to call.

        Args:
            player: Player for whom to calculate call amount

        Returns:
            float: Amount needed to call current bet
        """
        player_contribution = self.player_contributions.get(player, 0.0)
        call_amount = max(0, self.current_bet - player_contribution)
        return min(call_amount, player.stack)

    def get_total_pot_size(self) -> float:
        """Get the total pot size including all streets.

        Returns:
            float: Total pot size
        """
        return self.pot_previous_street + self.pot_current_street

    def _advance_street(self) -> None:
        """Advance to the next betting street.
        
        Moves current street pot to previous street pot and resets
        current street tracking for proper pot limit calculations.
        """
        # Move current street money to previous street
        self.pot_previous_street += self.pot_current_street
        self.pot_current_street = 0.0
        self.current_bet = 0.0
        
        # Reset player contributions for new street
        self.player_contributions.clear()


    def _update_pot_tracking(self, action: PlayerAction) -> None:
        """Update PLO-specific pot tracking after an action.

        Args:
            action: The action that was processed
        """
        if action.action_type in [
            PlayerActionType.BET,
            PlayerActionType.CALL,
            PlayerActionType.RAISE,
            PlayerActionType.ALLIN,
        ]:
            # Calculate current street pot from actual pot size minus previous streets
            total_pot = sum(pot.stack for pot in self.pots) if self.pots else 0.0
            self.pot_current_street = total_pot - self.pot_previous_street
            
            # Update current bet based on player contributions (managed by parent class)
            self.current_bet = max(self.player_contributions.values()) if self.player_contributions else 0.0

    def _validate_pot_limit_bet(self, action: PlayerAction) -> bool:
        """Validate pot-limit bet.

        Args:
            action: The bet action to validate

        Returns:
            bool: True if the bet is valid, False otherwise
        """
        if action.stack <= 0:
            return False

        # Can only bet if no current bet exists
        if self.current_bet > 0:
            return False

        # Check if bet exceeds pot limit
        max_bet = self.calculate_max_pot_limit_bet()
        if action.stack > max_bet:
            return False

        # Check if player has sufficient stack
        if action.stack > action.player.stack:
            return False

        return True

    def _validate_pot_limit_raise(self, action: PlayerAction) -> bool:
        """Validate pot-limit raise.

        Args:
            action: The raise action to validate

        Returns:
            bool: True if the raise is valid, False otherwise
        """
        if action.stack <= 0:
            return False

        # Player must have enough to call first
        call_amount = self.calculate_call_amount(action.player)
        if action.stack < call_amount:
            return False

        # Check against maximum pot-limit raise
        max_raise = self.calculate_max_pot_limit_raise(action.player)
        if action.stack > max_raise:
            return False

        return True

    def validate_omaha_hand(self, player_cards: List[int], board_cards: List[int]) -> bool:
        """Validate Omaha hand using exactly 2 hole cards + 3 board cards.

        Args:
            player_cards: List of player's hole card bitmasks
            board_cards: List of board card bitmasks

        Returns:
            bool: True if valid Omaha hand combination exists
        """
        if len(board_cards) < 3:
            return False  # Need at least 3 board cards
        
        if len(player_cards) < 2:
            return False  # Need at least 2 hole cards
        
        # Extract individual cards from bitmasks
        player_individual_cards = []
        for card_mask in player_cards:
            player_individual_cards.extend(extract_cards(card_mask))
        
        board_individual_cards = []
        for card_mask in board_cards:
            board_individual_cards.extend(extract_cards(card_mask))
        
        # Check if we can form a valid 5-card hand
        # Must use exactly 2 from hole cards and exactly 3 from board
        if len(player_individual_cards) >= 2 and len(board_individual_cards) >= 3:
            # Try all combinations of 2 hole cards with 3 board cards
            for hole_combo in combinations(player_individual_cards, 2):
                for board_combo in combinations(board_individual_cards, 3):
                    # Valid Omaha hand found
                    return True
        
        return False

    def register_action(self, action: PlayerAction) -> bool:
        """Register a player action with PLO-specific processing.

        Args:
            action: The action to register

        Returns:
            bool: True if action was successfully registered
        """
        # Perform base action registration
        success = super().register_action(action)
        
        if success:
            # Update PLO-specific pot tracking
            self._update_pot_tracking(action)
        
        return success