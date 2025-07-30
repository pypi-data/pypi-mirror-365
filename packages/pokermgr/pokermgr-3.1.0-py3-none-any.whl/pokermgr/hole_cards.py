"""Hole Cards Module

This module defines the HoleCards class, which represents a player's private cards in poker.
It provides functionality to analyze and categorize hole cards, including range codes
and properties like suitedness and connectivity.

Classes:
    HoleCards: Represents a player's private cards with analysis capabilities.
"""
from typing import List, Tuple
from dataclasses import dataclass, field
from cardspy.card import extract_cards
from pokermgr.funcs import get_range_codes, get_cards_properties


@dataclass(unsafe_hash=True)
class HoleCards:
    """Represents a player's private cards in a poker game.
    
    This class encapsulates the functionality to analyze and categorize a player's
    hole cards, including determining their range codes and properties like
    suitedness, connectivity, and paired status.
    
    Attributes:
        key: Integer bitmask representing the hole cards.
        ranges: List of poker range codes (e.g., ['AKs', 'AKo'] for Ace-King).
        properties: Bitmask representing properties of the hole cards:
                   - 0x8: Pair (both cards same rank)
                   - 0x4: Suited (both cards same suit)
                   - 0x2: Connected (ranks differ by 1, including A-2)
                   - 0x1: Two-card straight draw (part of any straight)
    
    Example:
        >>> from cardspy.deck import cards_to_mask
        >>> # Create hole cards with Ace-King suited
        >>> hole_cards = HoleCards(cards_to_mask(['Ah', 'Kh']))
        >>> print(f"Ranges: {hole_cards.ranges}")
        Ranges: ['AKs']
        >>> print(f"Is suited: {bool(hole_cards.properties & 0x4)}")
        Is suited: True
    """
    #: Integer bitmask representing the hole cards
    key: int
    
    #: Tuple of poker range codes (e.g., ('AKs', 'AKo'))
    ranges: Tuple[str, ...] = field(init=False)
    
    #: Bitmask representing properties of the hole cards
    properties: int = field(init=False)

    def __post_init__(self) -> None:
        """Initialize hole cards properties after instantiation.
        
        This method is automatically called by the dataclass after __init__
        to set up derived properties like ranges and card properties.
        """
        # Generate poker range codes (e.g., 'AKs' for Ace-King suited)
        self.ranges = tuple(get_range_codes(self.key))
        
        # Calculate card properties (suited, connected, etc.)
        self.properties = get_cards_properties(self.key)

    def __str__(self) -> str:
        cards = extract_cards(self.key)
        symbols = ""
        for card in cards:
            symbols += " " + card.symbol
        return symbols.strip()

    def __len__(self) -> int:
        """Return the number of hole cards.
        
        Returns:
            int: Number of cards in the hole cards
        """
        cards = extract_cards(self.key)
        return len(cards)
