"""Board"""

from dataclasses import dataclass, field
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from pokermgr.player import BoardPlayer, TablePlayer
from pokermgr.funcs import (
    get_connected,
    get_paired,
    get_suited,
    get_n_from_straight
)


@dataclass
class BoardTextureRank:
    """
    Analyzes and stores information about rank-based texture of the board.
    
    This class identifies paired cards on the board (pairs, three of a kind, etc.)
    which is crucial for evaluating hand strength and potential draws.
    
    Attributes:
        key: Integer representing the board cards (bitmask representation).
        paired_2: Bitmask of ranks that appear exactly twice on the board.
        paired_3: Bitmask of ranks that appear exactly three times on the board.
        paired_4: Bitmask of ranks that appear exactly four times on the board.
    """
    key: int
    paired_2: int = field(init=False)
    paired_3: int = field(init=False)
    paired_4: int = field(init=False)

    def __post_init__(self) -> None:
        """
        Initialize the paired attributes after the dataclass is instantiated.
        
        This method is automatically called by the dataclass after __init__.
        It calculates the paired attributes using the provided key.
        """
        self.paired_2 = get_paired(self.key, 2)
        self.paired_3 = get_paired(self.key, 3)
        self.paired_4 = get_paired(self.key, 4)


@dataclass
class BoardTextureSuit:
    """
    Analyzes and stores information about suit-based texture of the board.
    
    This class identifies potential flush opportunities by tracking suited cards.
    
    Attributes:
        key: Integer representing the board cards (bitmask representation).
        suited_2: Bitmask of suits that appear exactly twice on the board.
        suited_3: Bitmask of suits that appear exactly three times on the board.
        suited_4: Bitmask of suits that appear exactly four times on the board.
        suited_5: Bitmask of suits that appear exactly five times on the board.
    """
    key: int
    suited_2: int = field(init=False)
    suited_3: int = field(init=False)
    suited_4: int = field(init=False)
    suited_5: int = field(init=False)

    def __post_init__(self) -> None:
        """
        Initialize the suited attributes after the dataclass is instantiated.
        
        This method is automatically called by the dataclass after __init__.
        It calculates the suited attributes using the provided key.
        """
        self.suited_2 = get_suited(self.key, 2)
        self.suited_3 = get_suited(self.key, 3)
        self.suited_4 = get_suited(self.key, 4)
        self.suited_5 = get_suited(self.key, 5)


@dataclass
class BoardTextureStraight:
    """
    Analyzes and stores information about straight potential on the board.
    
    This class identifies connected cards and potential straight draws.
    
    Attributes:
        key: Integer representing the board cards (bitmask representation).
        connected_pairs: Bitmask of ranks that form connected pairs (e.g., 5-6, J-Q).
        two_from_straight: Bitmask of ranks that are two cards away from a straight.
        three_from_straight: Bitmask of ranks that are three cards away from a straight.
        four_from_straight: Bitmask of ranks that are four cards away from a straight.
        five_from_straight: Bitmask of ranks that are five cards away from a straight.
    """
    key: int
    connected_pairs: int = field(init=False)
    two_from_straight: int = field(init=False)
    three_from_straight: int = field(init=False)
    four_from_straight: int = field(init=False)
    five_from_straight: int = field(init=False)

    def __post_init__(self) -> None:
        """
        Initialize the straight-related attributes after the dataclass is instantiated.
        
        This method is automatically called by the dataclass after __init__.
        It calculates the straight potential attributes using the provided key.
        """
        self.connected_pairs = get_connected(self.key)
        self.two_from_straight = get_n_from_straight(self.key, 2)
        self.three_from_straight = get_n_from_straight(self.key, 3)
        self.four_from_straight = get_n_from_straight(self.key, 4)
        self.five_from_straight = get_n_from_straight(self.key, 5)


@dataclass
class BoardTexture:
    """
    Aggregates all texture information about the board.
    
    This class combines rank, suit, and straight analysis to provide a complete
    picture of the board's texture, which is crucial for hand evaluation.
    
    Attributes:
        key: Integer representing the board cards (bitmask representation).
        rank: BoardTextureRank instance for rank-based analysis.
        suit: BoardTextureSuit instance for suit-based analysis.
        straight: BoardTextureStraight instance for straight potential analysis.
    """
    key: int
    rank: BoardTextureRank = field(init=False)
    suit: BoardTextureSuit = field(init=False)
    straight: BoardTextureStraight = field(init=False)

    def __post_init__(self) -> None:
        """
        Initialize the texture analysis components after the dataclass is instantiated.
        
        This method is automatically called by the dataclass after __init__.
        It initializes all texture analysis components with the current board state.
        """
        self.rank = BoardTextureRank(self.key)
        self.suit = BoardTextureSuit(self.key)
        self.straight = BoardTextureStraight(self.key)


@dataclass
class Board:
    """
    Represents the community cards in a poker game.
    
    The Board class manages the community cards and provides access to texture analysis.
    It supports adding cards and automatically updates the texture analysis.
    
    Attributes:
        key: Integer representing the board cards (bitmask representation).
        cards: Current set of community cards (bitmask representation).
        texture: BoardTexture instance providing texture analysis.
        players: List of board players on this board.
        community_cards: List of community cards dealt to the board.
        
    Example:
        >>> board = Board(key=0x1a1)  # Initialize with a board key
        >>> board.add_cards(0x800)    # Add a card to the board
        >>> # The texture is automatically updated
        >>> print(f"Paired ranks: {board.texture.rank.paired_2}")
    """
    key: int
    cards: int = field(init=False)
    texture: BoardTexture = field(init=False)
    players: List["BoardPlayer"] = field(init=False, default_factory=list)
    community_cards: List[int] = field(init=False, default_factory=list)

    def __post_init__(self) -> None:
        """
        Initialize the board with empty cards and initial texture analysis.
        
        This method is automatically called by the dataclass after __init__.
        It sets up an empty board and initializes the texture analysis.
        """
        self.cards = 0
        self.texture = BoardTexture(self.key)

    def add_cards(self, cards: int) -> None:
        """
        Add one or more cards to the board and update the texture analysis.
        
        Args:
            cards: Integer bitmask representing the card(s) to add.
            
        Example:
            >>> board = Board(key=0x1a1)
            >>> board.add_cards(0x800)  # Add a single card
            >>> board.add_cards(0x1000 | 0x2000)  # Add multiple cards at once
        """
        self.cards |= cards
        self.texture = BoardTexture(self.cards)
        # Store individual cards for easier access
        from cardspy.card import extract_cards
        card_list = extract_cards(cards)
        for card in card_list:
            if card.key not in self.community_cards:
                self.community_cards.append(card.key)

    def add_board_player(self, table_player: "TablePlayer", hole_cards: int) -> "BoardPlayer":
        """
        Add a table player to this board with their hole cards.
        
        Args:
            table_player: The table player to add
            hole_cards: The hole cards (as bitmask) for this player
            
        Returns:
            BoardPlayer: The created board player
        """
        from pokermgr.player import BoardPlayer, TablePlayer
        
        # Create a board player from the table player
        board_player: BoardPlayer = table_player.to_board_player()
        board_player.set_hole_cards(hole_cards)
        
        # Add to the board's player list
        self.players.append(board_player)
        
        return board_player
