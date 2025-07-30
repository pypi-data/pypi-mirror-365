"""Pot Limit Omaha Regular Game Simulator

This module implements the simulator for Pot Limit Omaha Regular games.
"""

from typing import List, Optional, Tuple, Dict, Any
from collections import deque
from pokermgr.game_simulator import GameSimulator
from pokermgr.table import Table
from pokermgr.player import TablePlayer
from pokermgr.action import GameActionType
from pokermgr.game_plo_regular import GamePLORegular


class GameSimulatorPLORegular(GameSimulator):
    """Simulator for Pot Limit Omaha Regular games.

    This class simulates Pot Limit Omaha Regular poker games with standard
    small blind and big blind structure and pot-limit betting.
    """

    def __init__(
        self,
        players: List[TablePlayer],
        small_blind: int = 1,
        big_blind: int = 2,
        hand_size: int = 4,
        board_count: int = 1,
        player_cards: Optional[List[Tuple[str]]] = None,
        board_cards: Optional[List[str]] = None,
        game_actions: Optional[List[Tuple[GameActionType, Dict[str, Any]]]] = None,
    ) -> None:
        """Initialize the PLO Regular game simulator.

        Args:
            players: List of table players
            small_blind: Small blind amount (default: 1)
            big_blind: Big blind amount (default: 2)
            hand_size: Number of hole cards per player (default: 4)
            board_count: Number of boards to play (default: 1)
            player_cards: Optional predetermined player hole cards in standard format
                         (e.g., [('A♥', 'K♦', 'Q♥', 'J♦'), ('T♣', '9♣', '8♣', '7♣')])
            board_cards: Optional predetermined board cards in standard format
                         (e.g., ['A♠', 'K♥', 'Q♦', '2♣', '3♥'])
            game_actions: Optional list of game actions to process
        """
        super().__init__(players, board_count, player_cards, board_cards, game_actions)
        self.small_blind = small_blind
        self.big_blind = big_blind
        self.hand_size = hand_size

    def _create_game(self) -> None:
        """Create a PLO Regular game instance."""
        # Create table from players
        table = Table("sim_table", deque(self.players))

        # Create PLO Regular game
        self.game = GamePLORegular(
            key=1,
            table=table,
            small_blind=self.small_blind,
            big_blind=self.big_blind,
            initial_board_count=self.board_count,
            hand_size=self.hand_size,
        )

