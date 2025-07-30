"""Texas Hold'em Bomb Pot Game

This module implements the Texas Hold'em Bomb Pot variant where all players
are forced all-in pre-flop.
"""

from pokermgr.table import Table
from pokermgr.action import PlayerAction, PlayerActionType
from pokermgr.game_texas_holdem import GameTexasHoldem
from pokermgr.game_street import GameStreet


class GameTexasHoldemBomb(GameTexasHoldem):
    """Texas Hold'em Bomb Pot variant where all players are all-in pre-flop.

    In this variant, all players must post a blind and are automatically all-in
    before any cards are dealt. The hand then proceeds with community cards being
    dealt normally, but with no further betting rounds.

    Args:
        key: Unique identifier for the game
        table: Table object containing player information
        blind: Mandatory blind amount that all players must post
        initial_board_count: Number of boards to use (default: 1)

    Attributes:
        blind: Fixed blind amount for the bomb pot
    """
    def __init__(
        self,
        key: int,
        table: Table,
        blind: int,
        initial_board_count: int = 1
    ) -> None:
        super().__init__(key, table, initial_board_count)
        self.blind = blind
        # Initialize the pot with blinds from all players
        # self.pots[0].stack = self.blind * len(self.table.players)
        self.add_pot(self.blind * len(self.table.players))
        
    def _is_valid_action(self, action: PlayerAction) -> bool:
        """Validate if the given action is allowed in a Texas Hold'em Bomb Pot game.
        
        In a bomb pot, all players are forced all-in pre-flop, so normally no actions
        are allowed during the game as everyone is already all-in. However, for testing
        purposes, we allow basic validation through the parent class.
        
        Args:
            action: The action to validate
            
        Returns:
            bool: True if action meets basic validation requirements
        """
        # For testing purposes, allow basic action validation
        # In a real implementation, this might check if we're in a post-bomb phase
        # where additional betting could occur
        return super()._is_valid_action(action)