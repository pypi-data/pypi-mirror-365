"""
This module provides the Pot class which represents a poker pot.

A Pot tracks the amount of chips in play during a poker hand, the players
eligible to win the pot, and the eventual winners of the pot.
"""
from dataclasses import dataclass
from typing import List
from pokermgr.player import TablePlayer


@dataclass
class Pot:
    """
    A class representing a poker pot in a poker game.

    The Pot class tracks the chips in play, the players who have contributed to the pot,
    and the eventual winners per board. For multi-board games, the pot is typically
    split equally between boards (e.g., $500 pot = $250 per board).

    Attributes:
        key: A unique identifier for the pot.
        stack: The total amount of chips in the pot.
        players: List of players who have contributed to this pot and are eligible to win it.
        board_count: Number of boards this pot will be split across (default 1).
        winners_by_board: Dict mapping board_id to list of winners for that board.

    Note:
        The `winners_by_board` dict is initialized as an empty dict in `__post_init__`
        since we can't use a mutable default argument in the field definition.
    """
    key: int
    stack: float
    players: List[TablePlayer]

    def __str__(self) -> str:
        """Return a string representation of the pot using its unique key."""
        return f"{self.key}"
