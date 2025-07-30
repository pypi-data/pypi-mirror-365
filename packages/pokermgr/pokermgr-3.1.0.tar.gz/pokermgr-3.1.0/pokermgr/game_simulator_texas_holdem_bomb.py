"""Texas Hold'em Bomb Pot Game Simulator

This module implements the simulator for Texas Hold'em Bomb Pot games.
"""

from typing import List, Optional, Tuple, Dict, Any
from collections import deque
from pokermgr.game_simulator import GameSimulator
from pokermgr.table import Table
from pokermgr.player import TablePlayer
from pokermgr.action import GameActionType
from pokermgr.game_texas_holdem_bomb import GameTexasHoldemBomb


class GameSimulatorTexasHoldemBomb(GameSimulator):
    """Simulator for Texas Hold'em Bomb Pot games.

    This class simulates Texas Hold'em Bomb Pot games where all players
    are forced to put in a predetermined amount preflop.
    """

    def __init__(
        self,
        players: List[TablePlayer],
        bomb_amount: int = 10,
        board_count: int = 1,
        player_cards: Optional[List[Tuple[str]]] = None,
        board_cards: Optional[List[str]] = None,
        game_actions: Optional[List[Tuple[GameActionType, Dict[str, Any]]]] = None,
    ) -> None:
        """Initialize the Texas Hold'em Bomb Pot game simulator.

        Args:
            players: List of table players
            bomb_amount: Bomb pot amount each player must put in (default: 10)
            board_count: Number of boards to play (default: 1)
            player_cards: Optional predetermined player hole cards in standard format
                         (e.g., [('A♥', 'K♦'), ('Q♣', 'J♠')])
            board_cards: Optional predetermined board cards in standard format
                         (e.g., ['A♠', 'K♥', 'Q♦', '2♣', '3♥'])
            game_actions: Optional list of game actions to process
        """
        super().__init__(players, board_count, player_cards, board_cards, game_actions)
        self.bomb_amount = bomb_amount

    def _create_game(self) -> None:
        """Create a Texas Hold'em Bomb Pot game instance."""
        # Create table from players
        table = Table("sim_table", deque(self.players))
        
        # Create Texas Hold'em Bomb game
        self.game = GameTexasHoldemBomb(
            key=1,
            table=table,
            blind=self.bomb_amount,  # Use 'blind' parameter name
            initial_board_count=self.board_count,
        )
