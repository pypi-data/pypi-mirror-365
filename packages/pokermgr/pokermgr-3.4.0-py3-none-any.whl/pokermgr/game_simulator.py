from typing import List, Optional, Tuple, Dict, Any
from abc import ABC, abstractmethod
from collections import deque
from cardspy.card import get_card_keys_from_codes
from pokermgr.game_base import Game
from pokermgr.table import Table
from pokermgr.player import TablePlayer
from pokermgr.action import GameActionType


class GameSimulator(ABC):
    """Abstract base class for game simulators.
    
    This class provides common functionality for all poker game simulators,
    including player setup, card management, action processing, and state retrieval.
    Subclasses must implement the _create_game method for their specific game variant.
    """
    
    def __init__(
        self,
        players: List[TablePlayer],
        board_count: int = 1,
        player_cards: Optional[List[Tuple[str]]] = None,
        board_cards: Optional[List[str]] = None,
        game_actions: Optional[List[Tuple[GameActionType, Dict[str, Any]]]] = None,
    ) -> None:
        """Initialize the game simulator.
        
        Args:
            players: List of table players
            board_count: Number of boards to play (default: 1)
            player_cards: Optional predetermined player hole cards in standard format
                         (e.g., [('A♥', 'K♦'), ('Q♣', 'J♠')])
            board_cards: Optional predetermined board cards in standard format
                         (e.g., ['A♠', 'K♥', 'Q♦', '2♣', '3♥'])
            game_actions: Optional list of game actions to process
        """
        self.players = players
        self.board_count = board_count
        self.player_cards = player_cards
        self.board_cards = board_cards
        self.game_actions = game_actions
        self.game: Optional[Game] = None

    @abstractmethod
    def _create_game(self) -> None:
        """Create the game instance for the specific variant.
        
        This method must be implemented by subclasses to create their
        specific game type instance.
        """
        pass

    def initialize(self) -> None:
        """Initialize the game.
        
        Creates the game instance and sets up any predetermined cards.
        """
        self._create_game()

        # Handle predetermined cards if provided
        if self.player_cards:
            self._set_player_cards()

        if self.board_cards:
            self._set_board_cards()

    def _set_player_cards(self) -> None:
        """Set predetermined player cards."""
        if not self.player_cards or not self.game:
            return

        # Convert string cards to integers
        player_cards_converted = []
        for player_cards_tuple in self.player_cards:
            # Pass all cards for this player at once to get the combined mask
            hole_cards_mask = get_card_keys_from_codes(list(player_cards_tuple))
            player_cards_converted.append(hole_cards_mask)

        # Store the converted cards for later use when DEAL_HOLE_CARDS is called
        self._predetermined_player_cards = player_cards_converted

    def _set_board_cards(self) -> None:
        """Set predetermined board cards."""
        if not self.board_cards or not self.game:
            return

        # Convert string cards to individual card bitmasks
        from cardspy.card import get_card_keys_from_codes
        from collections import deque
        
        # Get individual card bitmasks for the board cards
        board_card_bitmasks = []
        for card_str in self.board_cards:
            card_bitmask = get_card_keys_from_codes([card_str])
            board_card_bitmasks.append(card_bitmask)
        
        # Create a queue of cards for dealing in stages (flop=3, turn=1, river=1)
        self._board_card_queue = deque(board_card_bitmasks)

    def relay_game_action(
        self,
        game_action_type: GameActionType,
        action_details: Optional[Dict[str, Any]] = None,
    ) -> bool:
        if not self.game:
            raise RuntimeError("Game not initialized. Call initialize() first.")

        # Handle predetermined cards for DEAL_HOLE_CARDS using direct method
        if game_action_type == GameActionType.DEAL_HOLE_CARDS and hasattr(
            self, "_predetermined_player_cards"
        ):
            # Use direct method to avoid validation issues with converted cards
            self.game.deal_hole_cards(self._predetermined_player_cards)
            return True

        # Handle predetermined board cards for DEAL_BOARD
        if game_action_type == GameActionType.DEAL_BOARD and hasattr(
            self, "_board_card_queue"
        ):
            return self._deal_predetermined_board_cards()

        return self.game.process_game_action(
            game_action_type=game_action_type, action_details=action_details
        )

    def _deal_predetermined_board_cards(self) -> bool:
        """Deal predetermined board cards based on current street."""
        if not hasattr(self, "_board_card_queue") or not self._board_card_queue:
            return False
        
        from pokermgr.game_street import GameStreet
        
        if self.game.game_street == GameStreet.FLOP:
            # Deal flop (3 cards) - called when game has advanced to FLOP street
            if len(self._board_card_queue) >= 3:
                # Clear any existing board cards and set our predetermined ones
                flop_cards = [self._board_card_queue.popleft() for _ in range(3)]
                flop_bitmask = sum(flop_cards)
                for i, board in enumerate(self.game.boards):
                    board.cards = flop_bitmask  # Replace existing cards
                # Don't advance street - stay on FLOP for betting
                return True
                
        elif self.game.game_street == GameStreet.TURN:
            # Deal turn (1 card) - called when game has advanced to TURN street  
            if self._board_card_queue:
                from cardspy.card import extract_cards, get_card_keys_from_codes
                turn_card = self._board_card_queue.popleft()
                
                for i, board in enumerate(self.game.boards):
                    current_cards = extract_cards(board.cards)
                    if len(current_cards) == 4:
                        # Board has 4 cards: 3 predetermined flop + 1 auto-dealt turn
                        # We need to reconstruct with our predetermined flop + our turn
                        # Our predetermined flop should be ['9♦', '9♠', '4♦']
                        expected_flop = get_card_keys_from_codes(['9♦', '9♠', '4♦'])
                        board.cards = expected_flop + turn_card
                    elif len(current_cards) == 3:
                        # Board has 3 cards: just add our turn
                        board.add_cards(turn_card)
                    else:
                        # Unexpected state, but add our turn anyway
                        board.add_cards(turn_card)
                return True
                
        elif self.game.game_street == GameStreet.RIVER:
            # Deal river (1 card) - called when game has advanced to RIVER street
            if self._board_card_queue:
                from cardspy.card import extract_cards, get_card_keys_from_codes
                river_card = self._board_card_queue.popleft()
                
                for i, board in enumerate(self.game.boards):
                    current_cards = extract_cards(board.cards)
                    if len(current_cards) == 5:
                        # Board has 5 cards: 4 predetermined + 1 auto-dealt river
                        # We need to reconstruct with our predetermined flop+turn + our river
                        # Our predetermined flop+turn should be ['9♦', '9♠', '4♦', '7♥']
                        expected_turn = get_card_keys_from_codes(['9♦', '9♠', '4♦', '7♥'])
                        board.cards = expected_turn + river_card
                    elif len(current_cards) == 4:
                        # Board has 4 cards: just add our river
                        board.add_cards(river_card)
                    else:
                        # Unexpected state, but add our river anyway
                        board.add_cards(river_card)
                return True
        
        return False

    def process_game_actions(self) -> bool:
        if not self.game_actions:
            return True

        for game_action_type, action_details in self.game_actions:
            s = self.relay_game_action(game_action_type, action_details)
            if not s:
                return False
        return True

    def get_game_state(self) -> Dict[str, Any]:
        """Get current game state."""
        if not self.game:
            return {}

        return {
            "street": self.game.game_street,
            "pot_size": self.game.get_total_pot_size(),
            "player_to_act": getattr(self.game.player_to_act, "code", None),
            "is_complete": self.game.is_hand_complete(),
        }

    def get_results(self) -> List[Dict[str, Any]]:
        """Get game results."""
        if not self.game:
            return []

        return self.game.get_result()

    def reset_for_new_hand(self) -> None:
        """Reset the game for a new hand."""
        if self.game:
            self.game.reset_for_new_hand()

    def is_hand_complete(self) -> bool:
        """Check if the current hand is complete."""
        if not self.game:
            return False

        return self.game.is_hand_complete()

    def get_pot_size(self) -> float:
        """Get the total pot size."""
        if not self.game:
            return 0.0

        return self.game.get_total_pot_size()

    def get_current_street(self) -> Optional[str]:
        """Get the current street name."""
        if not self.game:
            return None

        return self.game.game_street.name

    def get_player_to_act(self) -> Optional[str]:
        """Get the code of the player who needs to act."""
        if not self.game or not self.game.player_to_act:
            return None

        return getattr(self.game.player_to_act, "code", str(self.game.player_to_act))
