"""Texas Hold'em Game Base Class

This module implements the base Texas Hold'em game class that provides
Texas Hold'em specific functionality including two-card hole card dealing.
"""

from pokermgr.table import Table
from pokermgr.action import PlayerAction, PlayerActionType
from pokermgr.game_base import Game
from pokermgr.player import PlayerStatus


class GameTexasHoldem(Game):
    """Base class for Texas Hold'em poker games.

    This class implements Texas Hold'em specific rules, including dealing
    two hole cards to each player. It serves as a base class for different
    Texas Hold'em variants (e.g., regular, bomb pots).

    Args:
        key: Unique identifier for the game
        table: Table object containing player information
        initial_board_count: Number of boards to use (default: 1)
    """
    def __init__(
        self,
        key: int,
        table: Table,
        initial_board_count: int = 1
    ) -> None:
        self.initial_board_count = initial_board_count
        super().__init__(key, table, initial_board_count)

    def _core_deal_hole_cards(self) -> None:
        """Deal two hole cards to each player from the deck.

        This implements the standard Texas Hold'em dealing where each player
        receives exactly two private cards.
        """
        for player in self.table.players:
            player.set_hole_cards(self.deck.deal_cards(2))
            
    def _is_valid_action(self, action: PlayerAction) -> bool:
        """Validate if the given action is allowed according to Texas Hold'em rules.
        
        This implements basic Texas Hold'em validation logic that is common
        across all Texas Hold'em variants.
        
        Args:
            action: The action to validate
            
        Returns:
            bool: True if the action is valid, False otherwise
        """
        # Player must not be folded, sitting out, or all-in
        if action.player.status in [PlayerStatus.FOLDED, PlayerStatus.SITOUT, PlayerStatus.ALLIN]:
            return False
        
        # Validate action based on type
        if action.action_type == PlayerActionType.FOLD:
            return True
            
        elif action.action_type == PlayerActionType.CHECK:
            # Can check if no bet to call OR if player has already matched the current bet
            current_bet = self._get_current_bet()
            player_contribution = self.player_contributions.get(action.player, 0.0)
            return current_bet == 0 or player_contribution >= current_bet
            
        elif action.action_type == PlayerActionType.CALL:
            # Must have a bet to call and action stack must match call amount
            current_bet = self._get_current_bet()
            if current_bet == 0:
                return False  # Nothing to call
            
            call_amount = self.calculate_call_amount(action.player)
            return (action.player.stack >= call_amount and 
                   action.stack == call_amount)
            
        elif action.action_type == PlayerActionType.BET:
            # Can only bet if no current bet exists
            return self._get_current_bet() == 0 and action.player.stack >= action.stack
            
        elif action.action_type == PlayerActionType.RAISE:
            # Must have a bet to raise and sufficient stack
            current_bet = self._get_current_bet()
            player_contribution = self.player_contributions.get(action.player, 0.0)
            total_after_raise = player_contribution + action.stack
            return (current_bet > 0 and 
                   action.player.stack >= action.stack and
                   total_after_raise > current_bet)
            
        elif action.action_type == PlayerActionType.ALLIN:
            # Player must have chips to go all-in
            return action.player.stack > 0
            
        return False
        
    def _get_current_bet(self) -> float:
        """Get the current bet amount that needs to be called.
        
        Returns:
            float: The current bet amount (highest total contribution)
        """
        if not hasattr(self, 'player_contributions') or not self.player_contributions:
            return 0.0
            
        # Return the highest total contribution in the current round
        return max(self.player_contributions.values()) if self.player_contributions else 0.0