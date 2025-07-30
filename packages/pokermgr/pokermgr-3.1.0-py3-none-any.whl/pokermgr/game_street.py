"""Game Street Enum

This module defines the GameStreet enum that represents the different streets
in a poker hand, including pre-flop, flop, turn, and river.
"""

from enum import Enum


class GameStreet(Enum):
    """Represents the different streets in a poker hand.

    Streets progress from pre-flop to river, with each street representing
    a different stage of the hand where community cards are revealed and
    betting occurs.

    Attributes:
        PRE_FLOP: Initial street where players receive hole cards
        FLOP: Second street where the first three community cards are dealt
        TURN: Third street where the fourth community card is dealt
        RIVER: Final street where the fifth community card is dealt
        SHOWDOWN: Final phase where remaining players show their hands
    """
    PRE_FLOP = 1  # Initial street with hole cards only
    FLOP = 2     # First three community cards
    TURN = 3     # Fourth community card
    RIVER = 4    # Fifth and final community card
    SHOWDOWN = 5 # Final phase where hands are revealed