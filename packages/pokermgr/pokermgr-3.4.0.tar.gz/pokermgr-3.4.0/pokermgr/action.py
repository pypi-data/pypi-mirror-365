"""
This module defines action classes and related enums for managing poker game actions.

It provides a structured way to represent:
1. Player actions - actions taken by players (fold, check, bet, call, raise, all-in)
2. Game actions - actions taken by the game system (deal cards, advance street, distribute pot, etc.)
"""

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Optional, Dict, Any
from datetime import datetime

if TYPE_CHECKING:
    from pokermgr.player import TablePlayer


class PlayerActionType(Enum):
    """
    Enum representing different types of actions a player can take in a poker game.
    
    Attributes:
        FOLD: Player folds their hand, forfeiting the current round
        CHECK: Player passes the action to the next player without betting (only if no bet to call)
        BET: Player places an initial wager in a betting round
        CALL: Player matches the current bet to stay in the hand
        RAISE: Player increases the current bet amount
        ALLIN: Player bets all of their remaining chips
    """
    FOLD = 0
    CHECK = 1
    BET = 2
    CALL = 3
    RAISE = 4
    ALLIN = 5


@dataclass
class PlayerAction:
    """
    Represents a single action taken by a player during a poker game.
    
    Attributes:
        player (TablePlayer): The player who performed the action
        action_type (PlayerActionType): The type of action taken (fold, check, bet, etc.)
        stack (float): The size of the bet or raise (if applicable), or the player's stack after the action
    """
    player: 'TablePlayer'
    action_type: PlayerActionType
    stack: float


class GameActionType(Enum):
    """
    Enum representing different types of external actions that applications can trigger.
    
    These are the only actions that external applications should use to interact
    with the game. All internal game flow (pot management, street advancement, 
    winner determination, etc.) happens automatically.
    
    Attributes:
        ACCEPT_BLINDS: Accept small/big blinds in regular games or bomb pot contributions
        DEAL_HOLE_CARDS: Deal hole cards to the players
        ACCEPT_PLAYER_ACTION: Accept and process a player action
        DEAL_BOARD: Deal community cards (flop/turn/river)
    """
    ACCEPT_BLINDS = 0
    DEAL_HOLE_CARDS = 1
    ACCEPT_PLAYER_ACTION = 2
    DEAL_BOARD = 3


@dataclass
class GameAction:
    """
    Represents a single action taken by the game system during a poker game.
    
    Attributes:
        action_type (GameActionType): The type of game action
        timestamp (datetime): When the action occurred
        details (Optional[dict]): Additional information about the action
    """
    action_type: GameActionType
    timestamp: datetime
    details: Optional[Dict[str, Any]] = None
