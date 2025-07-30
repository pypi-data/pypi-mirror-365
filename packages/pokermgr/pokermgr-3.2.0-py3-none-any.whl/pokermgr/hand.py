"""Poker Hand Module

This module defines the Hand class, which represents a poker hand in the game.
A hand consists of cards and associated metadata like hand type, weight, and draws.

Classes:
    Hand: Represents a poker hand with cards and associated metadata.
"""

from dataclasses import dataclass, field


@dataclass
class Hand:
    """Represents a poker hand with cards and associated metadata.

    This class stores information about a poker hand, including the cards it contains,
    the type of hand (pair, flush, etc.), its weight for comparison, and any potential
    draws. It's designed to work with bitmask representations of cards for efficiency.

    Attributes:
        cards: Integer bitmask representing the cards in the hand.
        type_key: Numeric identifier for the hand type (e.g., pair, flush).
        type_name: Human-readable name of the hand type.
        weight: Numeric value representing the hand's strength for comparison.
        draws: Bitmask representing potential draws (e.g., flush draw, straight draw).
        range_code: Poker hand range code (e.g., 'AKs' for Ace-King suited).

    Example:
        >>> from cardspy.deck import cards_to_mask
        >>> # Create a hand with Ace-King suited
        >>> hand = Hand(cards_to_mask(['Ah', 'Kh']))
        >>> hand.type_key = 1  # Example: pair
        >>> hand.type_name = "Pair"
        >>> hand.weight = 1000
    """

    #: Bitmask representing the cards in the hand
    cards: int

    #: Numeric identifier for the hand type (e.g., pair, flush)
    type_key: int = field(init=False)

    #: Human-readable name of the hand type
    type_name: str = field(init=False)

    #: Numeric value representing the hand's strength
    weight: int = field(init=False)

    #: Bitmask representing potential draws (flush, straight, etc.)
    draws: int = field(init=False)

    #: Poker hand range code (e.g., 'AKs' for Ace-King suited)
    range_code: str = field(init=False)

    def __post_init__(self) -> None:
        """Initialize the hand with default values after instantiation.

        This method is automatically called by the dataclass after __init__
        to set up default values for fields that shouldn't be in the constructor.
        """
        self.type_key = 0  # Default to high card
        self.type_name = "High Card"  # Default hand type name
        self.weight = 0  # Default weight (will be calculated)
        self.draws = 0  # No draws by default
        self.range_code = ""  # Will be set based on hole cards
