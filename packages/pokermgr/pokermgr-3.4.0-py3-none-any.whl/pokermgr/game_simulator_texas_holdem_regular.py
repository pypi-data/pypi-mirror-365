"""Texas Hold'em Regular Game Simulator

This module implements the simulator for Texas Hold'em Regular games.
"""

from typing import List, Optional, Tuple, Dict, Any
from collections import deque
from pokermgr.game_simulator import GameSimulator
from pokermgr.table import Table
from pokermgr.player import TablePlayer
from pokermgr.action import GameActionType
from pokermgr.game_texas_holdem_regular import GameTexasHoldemRegular


class GameSimulatorTexasHoldemRegular(GameSimulator):
    """Simulator for Texas Hold'em Regular games.

    This class simulates Texas Hold'em Regular poker games with standard
    small blind and big blind structure.
    """

    def __init__(
        self,
        players: List[TablePlayer],
        small_blind: int = 1,
        big_blind: int = 2,
        board_count: int = 1,
        player_cards: Optional[List[Tuple[str]]] = None,
        board_cards: Optional[List[str]] = None,
        game_actions: Optional[List[Tuple[GameActionType, Dict[str, Any]]]] = None,
    ) -> None:
        """Initialize the Texas Hold'em Regular game simulator.

        Args:
            players: List of table players
            small_blind: Small blind amount (default: 1)
            big_blind: Big blind amount (default: 2)
            board_count: Number of boards to play (default: 1)
            player_cards: Optional predetermined player hole cards in standard format
                         (e.g., [('A♥', 'K♦'), ('Q♣', 'J♠')])
            board_cards: Optional predetermined board cards in standard format
                         (e.g., ['A♠', 'K♥', 'Q♦', '2♣', '3♥'])
            game_actions: Optional list of game actions to process
        """
        super().__init__(players, board_count, player_cards, board_cards, game_actions)
        self.small_blind = small_blind
        self.big_blind = big_blind

    def _create_game(self) -> None:
        """Create a Texas Hold'em Regular game instance."""
        # Create table from players
        table = Table("sim_table", deque(self.players))

        # Create Texas Hold'em Regular game
        self.game = GameTexasHoldemRegular(
            key=1,
            table=table,
            small_blind=self.small_blind,
            big_blind=self.big_blind,
            initial_board_count=self.board_count,
        )

