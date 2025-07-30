"""Player module for poker game.

This module defines the core player-related classes for a poker game, including:
- PlayerStatus: Enum for different player states
- Player: Base player class with bankroll management
- TablePlayer: Extended player class for table gameplay
- BoardPlayer: Extended player class for board-specific gameplay
"""
from dataclasses import dataclass, field, asdict, fields
from enum import Enum
from typing import Optional, TypeVar
from pokermgr.hole_cards import HoleCards
from pokermgr.hand import Hand
from pokermgr.action import PlayerAction, PlayerActionType

# Type variable for generic return type in class methods
T = TypeVar('T', bound='Player')


class PlayerStatus(Enum):
    """Enum representing the possible statuses of a poker player.

    Attributes:
        INGAME: Player is actively playing the current hand
        SITOUT: Player is sitting out the current hand
        FOLDED: Player has folded their hand
        ALLIN: Player is all-in and cannot make further bets
    """
    INGAME = 0x1
    SITOUT = 0x2
    FOLDED = 0x4
    ALLIN = 0x8


@dataclass
class Player:
    """Base class representing a poker player.

    Attributes:
        code: Unique identifier for the player
        bank_roll: Current amount of money the player has (default: 3000)
    """
    code: str
    bank_roll: float = field(default=3000.0)

    def add_balance(self, amount: float) -> None:
        """Add funds to the player's bank roll.

        Args:
            amount: The amount to add to the bank roll

        Note:
            No validation is performed on the amount. It can be negative.
        """
        self.bank_roll += amount

    def remove_balance(self, amount: float) -> None:
        """Remove funds from the player's bank roll.

        Args:
            amount: The amount to remove from the bank roll

        Note:
            No validation is performed on the amount. It can be negative.
        """
        self.bank_roll -= amount

    def __str__(self) -> str:
        """Return the player's code as string representation.

        Returns:
            str: The player's unique code
        """
        return self.code

    def __repr__(self) -> str:
        """Return the player's code as the official string representation.

        Returns:
            str: The player's unique code
        """
        return self.code

    def __eq__(self, other: object) -> bool:
        """Compare two Player instances for equality.

        Args:
            other: The object to compare with

        Returns:
            bool: True if other is a Player with the same code, False otherwise
        """
        if not isinstance(other, Player):
            return False
        return self.code == other.code

    def __hash__(self) -> int:
        """Return hash value for Player instance.

        Returns:
            int: Hash value based on player code
        """
        return hash(self.code)


@dataclass
class TablePlayer(Player):
    """Extended Player class for table gameplay with hand and betting management.

    Attributes:
        status: Current status of the player in the game
        hole_cards: Bitmask representing the player's hole cards
        equity: The player's current equity in the hand (0.0 to 1.0)
        current_bet: The amount the player has bet in the current betting round
        stack: The player's current chip stack
        last_action: The player's last action in the current hand
    """
    stack: float = field(default=150.0)  # Accept stack as constructor parameter
    status: PlayerStatus = field(default=PlayerStatus.INGAME, init=False)
    hole_cards: HoleCards = field(init=False, default_factory=lambda: HoleCards(0))
    equity: float = field(init=False, default=0.0)
    current_bet: float = field(init=False, default=0.0)
    last_action: Optional[PlayerAction] = field(init=False, default=None)

    def __post_init__(self) -> None:
        """Initialize TablePlayer instance with default values."""
        self.status = PlayerStatus.INGAME
        self.hole_cards = HoleCards(0)
        self.equity = 0.0
        self.current_bet = 0.0
        self.last_action = None

    def set_hole_cards(self, cards: int) -> None:
        """Set the player's hole cards and update the best hand.

        This method creates a new HoleCards instance with the given card mask
        and updates the player's best hand to use these new hole cards.

        Args:
            cards: Integer bitmask representing the hole cards

        Example:
            >>> from cardspy.deck import cards_to_mask
            >>> player = TablePlayer("p1")
            >>> player.set_hole_cards(cards_to_mask(['As', 'Ks']))
            >>> print(player.hole_cards.ranges)
            ['AKs']
        """
        self.hole_cards = HoleCards(cards)

    def add_stack(self, amount: float) -> None:
        """Add chips to the player's stack from their bank roll.

        This method transfers the specified amount from the player's bank roll
        to their current stack. The amount must be non-negative and cannot exceed
        the player's available bank roll.

        Args:
            amount: The number of chips to add to the stack (must be >= 0)

        Raises:
            ValueError: If amount is negative or exceeds bank roll

        Example:
            >>> player = TablePlayer("p1")
            >>> player.bank_roll = 1000.0
            >>> player.stack = 100.0
            >>> player.add_stack(200.0)
            >>> player.stack
            300.0
            >>> player.bank_roll
            800.0
        """
        if amount <= 0:
            raise ValueError("Cannot add zero or negative amount to stack")
        if self.bank_roll < amount:
            raise ValueError("Not enough bank roll")
        self.stack += amount
        self.bank_roll -= amount

    def remove_stack(self, amount: float) -> None:
        """Remove chips from the player's stack and return to bank roll.

        This method transfers the specified amount from the player's current stack
        back to their bank roll. The amount must be non-negative and cannot exceed
        the player's current stack.

        Args:
            amount: The number of chips to remove from the stack (must be >= 0)

        Raises:
            ValueError: If amount is negative or exceeds current stack

        Example:
            >>> player = TablePlayer("p1")
            >>> player.stack = 500.0
            >>> player.bank_roll = 1000.0
            >>> player.remove_stack(200.0)
            >>> player.stack
            300.0
            >>> player.bank_roll
            1200.0
        """
        if amount <= 0:
            raise ValueError("Cannot remove zero or negative amount from stack")
        if self.stack < amount:
            raise ValueError("Not enough stack")
        self.stack -= amount
        self.bank_roll += amount

    def fold(self) -> PlayerAction:
        """Execute a fold action.

        Returns:
            PlayerAction: The fold action that was taken

        Note:
            Sets the player's status to FOLDED and records the action
        """
        self.status = PlayerStatus.FOLDED
        self.last_action = PlayerAction(player=self, action_type=PlayerActionType.FOLD, stack=0.0)
        return self.last_action

    def check(self) -> PlayerAction:
        """Execute a check action.

        Returns:
            PlayerAction: The check action that was taken

        Note:
            Records the check action. Does not change the player's status.
        """
        self.last_action = PlayerAction(player=self, action_type=PlayerActionType.CHECK, stack=0.0)
        return self.last_action

    def __str__(self) -> str:
        """Return a string representation of the player."""
        return self.code

    def __repr__(self) -> str:
        """Return a string representation of the player."""
        return self.code

    def __eq__(self, other: object) -> bool:
        """Return True if the players are equal."""
        if not isinstance(other, Player):
            return False
        return self.code == other.code

    def to_board_player(self) -> "BoardPlayer":
        # 1) Build with only the args BoardPlayer actually accepts:
        init_fields = {f.name for f in fields(BoardPlayer) if f.init}
        data = asdict(self)
        kwargs = {k: data[k] for k in init_fields}
        bp = BoardPlayer(**kwargs)

        # 2) Now manually copy whatever else you care about:
        for attr in ("status", "hole_cards", "equity", "current_bet", "stack", "last_action"):
            setattr(bp, attr, getattr(self, attr))
        return bp

    def __hash__(self) -> int:
        """Return hash value for TablePlayer instance.

        Returns:
            int: Hash value based on player code (inherited from Player)
        """
        return super().__hash__()


@dataclass
class BoardPlayer(TablePlayer):
    """A player on the table with a hole card and a best hand."""
    hand: Hand = field(init=False)

    def __str__(self) -> str:
        return self.code

    def __repr__(self) -> str:
        return self.code
