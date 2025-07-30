"""Base Game Class

This module implements the base Game class providing common functionality
for all poker game variants. It handles core game flow, card dealing,
board management, and state tracking.
"""

from datetime import datetime
from enum import Enum
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from copy import deepcopy
from cardspy.card import extract_cards, get_card_keys_from_codes
from cardspy.deck import Deck
from pokermgr.table import Table
from pokermgr.pot import Pot
from pokermgr.board import Board
from pokermgr.player import TablePlayer, PlayerStatus
from pokermgr.evaluate import get_winners
from pokermgr.action import PlayerAction, PlayerActionType, GameAction, GameActionType
from pokermgr.game_street import GameStreet
from pokermgr.board import BoardTexture


class GameType(Enum):
    """Type of Poker Games"""

    TEXAS_HOLDEM_REGULAR = "Texas Hold'em Regular"
    TEXAS_HOLDEM_BOMB = "Texas Hold'em Bomb Pot"
    OMAHA_REGULAR = "Omaha Regular"
    OMAHA_BOMB = "Omaha Bomb Pot"


class Game(ABC):
    """Base class for poker games providing common functionality.

    This class handles the core game flow, including dealing cards, managing
    the board, and tracking game state. It serves as the foundation for
    different poker variants through inheritance.

    Args:
        key: Unique identifier for the game
        table: Table object containing player information
        initial_board_count: Number of boards to use (default: 1)

    Attributes:
        key: Unique game identifier
        table: Reference to the game table
        initial_board_count: Number of boards in play
        board_count: Current number of active boards
        boards: List of Board objects
        game_street: Current street of the game (from GameStreet enum)
        pots: List of active pots
        deck: Deck of cards
        player_to_act: Reference to the player whose turn it is to act
    """

    def __init__(self, key: int, table: Table, initial_board_count: int = 1) -> None:
        self.key = key
        self.table = table
        self.initial_board_count = initial_board_count
        self.board_count = 0
        self.boards: list[Board] = []
        self.game_street = GameStreet.PRE_FLOP
        self.pots: list[Pot] = []
        self.deck = Deck()
        self.player_to_act = self.table.players[0]
        self.game_actions: List[GameAction] = []
        # Cache for actions property to maintain object identity
        self._actions_cache: List[PlayerAction] = []
        self._actions_cache_version: int = 0
        # Track player contributions in current betting round
        self.player_contributions: Dict[TablePlayer, float] = {}
        # Track players who have acted in current betting round
        self.players_acted_this_round: set[TablePlayer] = set()
        # State snapshot for undo functionality
        self.state_snapshot: Optional[Dict[str, Any]] = None
        # Alias for backward compatibility with tests
        self._previous_state: Optional[Dict[str, Any]] = None
        self.initiate_board()

    @property
    def actions(self) -> List[PlayerAction]:
        """Get list of player actions from game_actions for backward compatibility.

        Returns:
            List[PlayerAction]: List of player actions extracted from game_actions
        """
        # Return the cached actions to maintain object identity
        return self._actions_cache

    @actions.setter
    def actions(self, value: List[PlayerAction]) -> None:
        """Set list of player actions by updating game_actions for backward compatibility.

        Args:
            value: List of player actions to set
        """
        # Clear existing ACCEPT_PLAYER_ACTION game actions
        self.game_actions = [
            ga
            for ga in self.game_actions
            if ga.action_type != GameActionType.ACCEPT_PLAYER_ACTION
        ]

        # Add new player actions as game actions
        for action in value:
            game_action = GameAction(
                action_type=GameActionType.ACCEPT_PLAYER_ACTION,
                timestamp=datetime.now(),
                details={"player_action": action},
            )
            self.game_actions.append(game_action)

        # Update cache
        self._actions_cache = value.copy()
        self._actions_cache_version += 1

    def initiate_board(self) -> None:
        """Initialize the specified number of boards for the game.

        This method creates the initial set of boards based on the
        initial_board_count. Each board will be assigned a unique ID.
        """
        while len(self.boards) < self.initial_board_count:
            self.add_board()

    def add_board(self) -> None:
        """Add a new board to the game.

        If boards already exist, the new board will be a copy of the most recent board.
        This ensures all boards are in sync when a new one is added mid-hand.
        Also updates all pots to track the new board.
        """
        # Create new board with incremented ID
        board_id = self.board_count + 1
        board = Board(board_id)

        # If boards exist, copy cards from the most recent board
        if self.board_count > 0:
            existing_board = self.boards[-1]
            board.add_cards(existing_board.cards)

        self.boards.append(board)
        self.board_count += 1

    def add_pot(
        self, stack: int = 0, players: Optional[List[TablePlayer]] = None
    ) -> Pot:
        """Add a new pot to the game (e.g., side pots when players go all-in).

        Args:
            stack: Initial amount of chips for the new pot.
            players: Iterable of players eligible for the pot. Defaults to all current players.
        Returns:
            The newly created Pot object.
        """
        if players is None:
            players = list(self.table.players)
        key = len(self.pots) + 1
        new_pot = Pot(key, stack, players)
        self.pots.append(new_pot)

        # Side pot creation happens automatically - no external tracking needed

        return new_pot

    def deal_hole_cards(self, cards: Optional[List[int]] = None) -> None:
        """Deal hole cards to all players.

        Args:
            cards: Optional list of pre-determined cards to deal. If not provided,
                  cards will be dealt randomly from the deck.

        Raises:
            ValueError: If called on any street other than pre-flop or if the number
                     of provided cards doesn't match the number of players.
        """
        if self.game_street != GameStreet.PRE_FLOP:
            raise ValueError("Hole cards can only be dealt on the pre-flop")

        if cards:
            # Deal specified cards if provided (for testing/deterministic dealing)
            if len(cards) != len(self.table.players):
                raise ValueError("Number of cards must match number of players")
            for player in self.table.players:
                player.set_hole_cards(cards.pop(0))
        else:
            # Use the game-specific dealing logic
            self._core_deal_hole_cards()

        # Hole card dealing tracked only via external process_game_action

    @abstractmethod
    def _core_deal_hole_cards(self) -> None:
        """Abstract method to handle game-specific hole card dealing logic.

        This method must be implemented by subclasses to define how hole cards
        are dealt for specific poker variants (e.g., 2 cards for Texas Hold'em,
        4 cards for Omaha, etc.).
        """

    @abstractmethod
    def _is_valid_action(self, action: PlayerAction) -> bool:
        """Validate if the given action is allowed according to game rules.

        This method must be implemented by subclasses to define game-specific
        validation logic for player actions. Common validations include:
        - Player has sufficient stack for the action
        - Action type is valid for current game state
        - Bet/raise amounts meet minimum requirements
        - Player is not folded or all-in already

        Args:
            action: The action to validate

        Returns:
            bool: True if the action is valid, False otherwise
        """

    def _is_player_turn(self, player: TablePlayer) -> bool:
        """Check if it's the specified player's turn to act.

        Args:
            player: The player to check

        Returns:
            bool: True if it's the player's turn, False otherwise
        """
        return self.player_to_act == player

    def _update_player_stack(self, action: PlayerAction) -> None:
        """Update the player's stack based on their action.

        Args:
            action: The action to process
        """
        if action.action_type in [
            PlayerActionType.BET,
            PlayerActionType.CALL,
            PlayerActionType.RAISE,
            PlayerActionType.ALLIN,
        ]:
            action.player.stack -= action.stack
            # Track player contribution in current round
            if action.player not in self.player_contributions:
                self.player_contributions[action.player] = 0.0
            self.player_contributions[action.player] += action.stack
            # Ensure stack doesn't go negative
            if action.player.stack < 0:
                action.player.stack = 0

    def _update_pot(self, action: PlayerAction) -> None:
        """Update the pot with the action amount.

        Args:
            action: The action to process
        """
        if action.action_type in [
            PlayerActionType.BET,
            PlayerActionType.CALL,
            PlayerActionType.RAISE,
            PlayerActionType.ALLIN,
        ]:
            # If no pots exist, create the main pot
            if not self.pots:
                self.add_pot(0)

            # Add amount to the main pot
            self.pots[0].stack += action.stack

    def _update_player_status(self, action: PlayerAction) -> None:
        """Update the player's status based on their action.

        Args:
            action: The action to process
        """
        if action.action_type == PlayerActionType.FOLD:
            action.player.status = PlayerStatus.FOLDED
        elif action.action_type == PlayerActionType.ALLIN or action.player.stack == 0:
            action.player.status = PlayerStatus.ALLIN
        else:
            action.player.status = PlayerStatus.INGAME

    def _set_player_to_act(self) -> None:
        """Set the next player to act."""
        if not self.table.players:
            self.player_to_act = None
            return

        # Find current player index
        try:
            current_index = self.table.players.index(self.player_to_act)
        except ValueError:
            # Player not in table, start with first player
            current_index = -1

        # Find next active player
        next_index = (current_index + 1) % len(self.table.players)
        start_index = next_index

        while self.table.players[next_index].status in [
            PlayerStatus.FOLDED,
            PlayerStatus.ALLIN,
            PlayerStatus.SITOUT,
        ]:
            next_index = (next_index + 1) % len(self.table.players)
            # If we've wrapped around to the start, no active players
            if next_index == start_index:
                self.player_to_act = None
                return

        self.player_to_act = self.table.players[next_index]

    def _track_game_action(
        self, action_type: GameActionType, details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Track a game action taken by the system.

        Args:
            action_type: The type of game action
            details: Optional details about the action
        """
        game_action = GameAction(
            action_type=action_type, timestamp=datetime.now(), details=details
        )
        self.game_actions.append(game_action)

    def _handle_auto_progression(self) -> None:
        """Handle automatic game progression after an action."""
        # 1. Check if only one player remains (all others folded) → declare winner
        active_players = [
            p
            for p in self.table.players
            if p.status not in [PlayerStatus.FOLDED, PlayerStatus.SITOUT]
        ]

        if len(active_players) <= 1:
            # Game ends - only one player left
            self.game_street = GameStreet.SHOWDOWN
            return

        # 2. Check if all remaining players are all-in → skip to showdown
        all_in_or_folded = all(
            p.status in [PlayerStatus.ALLIN, PlayerStatus.FOLDED, PlayerStatus.SITOUT]
            for p in self.table.players
        )

        if all_in_or_folded and len(active_players) > 1:
            # All players are all-in, skip remaining betting rounds
            self._skip_to_showdown()
            return

        # 3. Check if betting round is complete → advance to next street
        if self._is_betting_round_complete():
            self._advance_to_next_street()

    def _skip_to_showdown(self) -> None:
        """Skip remaining betting rounds and go directly to showdown."""
        # Deal remaining community cards if needed
        while self.game_street != GameStreet.SHOWDOWN:
            if self.game_street == GameStreet.PRE_FLOP:
                self.advance_to_flop()
            elif self.game_street == GameStreet.FLOP:
                self.advance_to_turn()
            elif self.game_street == GameStreet.TURN:
                self.advance_to_river()
            elif self.game_street == GameStreet.RIVER:
                self.advance_to_showdown()
                break

    def _advance_to_next_street(self) -> None:
        """Advance to the next street and reset betting round state."""
        if self.game_street == GameStreet.PRE_FLOP:
            self.advance_to_flop()
        elif self.game_street == GameStreet.FLOP:
            self.advance_to_turn()
        elif self.game_street == GameStreet.TURN:
            self.advance_to_river()
        elif self.game_street == GameStreet.RIVER:
            self.advance_to_showdown()

        # Reset betting round state for new street
        self._reset_betting_round()

        # Street advancement happens automatically - no external tracking needed

    def _reset_betting_round(self) -> None:
        """Reset betting round state for a new street."""
        # Clear player contributions for the new betting round
        self.player_contributions.clear()

        # Clear players who acted in previous round
        self.players_acted_this_round.clear()

        # Set first player to act for post-flop streets
        if self.game_street in [GameStreet.FLOP, GameStreet.TURN, GameStreet.RIVER]:
            self._set_first_postflop_player()

        # Reset any game-specific betting round state
        self._reset_additional_betting_state()

    def _reset_additional_betting_state(self) -> None:
        """Reset additional betting state - can be overridden by subclasses."""
        raise NotImplementedError(
            "Subclasses must implement _reset_additional_betting_state to handle game-specific logic."
        )

    def _set_first_postflop_player(self) -> None:
        """Set the first player to act in post-flop streets."""
        # In post-flop, first active player after dealer button acts first
        # For simplicity, we'll use the first active player
        for player in self.table.players:
            if player.status == PlayerStatus.INGAME:
                self.player_to_act = player
                return

        # No active players
        self.player_to_act = None

    def _change_street(self) -> None:
        """Change to the next street (stub implementation)."""
        raise NotImplementedError(
            "Subclasses must implement _change_street to handle street progression."
        )

    def register_action(self, action: PlayerAction) -> bool:
        """Register a player action in the game.

        This is the main method for handling player actions. It validates the action,
        updates game state, and records the action history.

        Args:
            action: The action to register

        Returns:
            bool: True if action was successfully registered, False otherwise
        """
        # Check if it's the player's turn
        if not self._is_player_turn(action.player):
            return False

        # Validate the action according to game rules
        if not self._is_valid_action(action):
            return False

        # Save state snapshot before processing the action
        self._save_state_snapshot()

        # Update player stack based on the action
        self._update_player_stack(action)

        # Update pot with the action amount
        self._update_pot(action)

        # Track that this player has acted in this betting round
        self.players_acted_this_round.add(action.player)

        # Update player status based on action
        self._update_player_status(action)

        # Track this player action in game_actions for backward compatibility
        game_action = GameAction(
            action_type=GameActionType.ACCEPT_PLAYER_ACTION,
            timestamp=datetime.now(),
            details={"player_action": action},
        )
        self.game_actions.append(game_action)

        # Update the actions cache to maintain object identity
        self._actions_cache.append(action)
        self._actions_cache_version += 1

        # Set next player to act
        self._set_player_to_act()

        # Check for automatic game progression after the action
        self._handle_auto_progression()

        return True

    # Note: add_action method removed - use process_game_action with ACCEPT_PLAYER_ACTION instead

    def deal_flop(self, cards: Optional[List[int]] = None) -> None:
        """Deal the flop (first three community cards).

        Args:
            cards: Optional list of pre-determined cards to deal as the flop.
                  If provided, must contain one card per board.

        Raises:
            ValueError: If called on any street other than pre-flop or if the
                     number of provided cards doesn't match the number of boards.
        """
        if self.game_street != GameStreet.PRE_FLOP:
            raise ValueError("Flop can only be dealt on the pre-flop")

        if cards:
            # Deal specified cards if provided (for testing/deterministic dealing)
            if len(cards) != self.board_count:
                raise ValueError("Number of cards must match number of boards")
            for board in self.boards:
                board.add_cards(cards.pop(0))
        else:
            # Deal random cards from the deck
            for board in self.boards:
                board.add_cards(self.deck.deal_cards(3))

        # Advance game state to FLOP
        self.game_street = GameStreet.FLOP

    def deal_turn(self, cards: Optional[List[int]] = None) -> None:
        """Deal the turn (fourth community card).

        Args:
            cards: Optional list of pre-determined cards to deal as the turn.
                  If provided, must contain one card per board.

        Raises:
            ValueError: If called on any street other than flop or if the
                     number of provided cards doesn't match the number of boards.
        """
        if self.game_street != GameStreet.FLOP:
            raise ValueError("Turn can only be dealt on the flop")
        if cards:
            if len(cards) != self.board_count:
                raise ValueError("Number of cards must match number of boards")
            for board in self.boards:
                board.add_cards(cards.pop(0))
        else:
            for board in self.boards:
                board.add_cards(self.deck.deal_cards(1))
        self.game_street = GameStreet.TURN

    def deal_river(self, cards: Optional[List[int]] = None) -> None:
        """Deal the river (fifth community card).

        Args:
            cards: Optional list of pre-determined cards to deal as the river.
                  If provided, must contain one card per board.

        Raises:
            ValueError: If called on any street other than turn or if the
                     number of provided cards doesn't match the number of boards.
        """
        if self.game_street != GameStreet.TURN:
            raise ValueError("River can only be dealt on the turn")
        if cards:
            if len(cards) != self.board_count:
                raise ValueError("Number of cards must match number of boards")
            for board in self.boards:
                board.add_cards(cards.pop(0))
        else:
            for board in self.boards:
                board.add_cards(self.deck.deal_cards(1))
        self.game_street = GameStreet.RIVER

    def get_total_pot_size(self) -> float:
        """Get the total size of all pots combined.

        Returns:
            float: Total pot size including all side pots
        """
        return sum(pot.stack for pot in self.pots)

    def get_side_pots(self) -> List[Pot]:
        """Get all side pots created by all-in situations.

        Returns:
            List[Pot]: List of all pots (main pot + side pots)
        """
        return self.pots.copy()

    def add_dead_money(self, amount: float) -> None:
        """Add dead money to the pot.

        Args:
            amount: Amount of dead money to add
        """
        if not self.pots:
            self.add_pot(0)
        self.pots[0].stack += amount

    def reset_for_new_hand(self) -> None:
        """Reset game state for a new hand."""
        self.game_actions.clear()  # Clear game actions instead of player actions
        self._actions_cache.clear()  # Clear the actions cache
        self._actions_cache_version += 1
        self.pots.clear()
        self.player_contributions.clear()
        self.players_acted_this_round.clear()
        self.state_snapshot = None
        self._previous_state = None
        self.game_street = GameStreet.PRE_FLOP
        # Reset player to act to first player
        if self.table.players:
            self.player_to_act = self.table.players[0]
        # Reset player statuses to INGAME (except SITOUT)
        for player in self.table.players:
            if player.status != PlayerStatus.SITOUT:
                player.status = PlayerStatus.INGAME

    def advance_to_flop(self, burn_card: bool = False) -> None:
        """Advance the game to the flop street.

        Args:
            burn_card: If True, burn a card before dealing flop
        """
        self.game_street = GameStreet.FLOP

        # Burn a card if requested
        if burn_card:
            self.deck.deal_cards(1)

        # Deal community cards for flop if boards don't have cards yet
        for board in self.boards:
            if board.cards == 0:  # No cards on board yet
                board.add_cards(self.deck.deal_cards(3))

        # Reset betting round for new street
        self._reset_betting_round()

        # Board dealing tracked only via external process_game_action

    def advance_to_turn(self, burn_card: bool = False) -> None:
        """Advance the game to the turn street.

        Args:
            burn_card: If True, burn a card before dealing turn
        """
        self.game_street = GameStreet.TURN

        # Burn a card if requested
        if burn_card:
            self.deck.deal_cards(1)

        # Deal turn card if needed
        for board in self.boards:
            # Count existing cards (approximately)
            if (
                board.cards > 0 and len(board.community_cards) == 3
            ):  # Has flop but not turn
                board.add_cards(self.deck.deal_cards(1))

        # Reset betting round for new street
        self._reset_betting_round()

        # Board dealing tracked only via external process_game_action

    def advance_to_river(self, burn_card: bool = False) -> None:
        """Advance the game to the river street.

        Args:
            burn_card: If True, burn a card before dealing river
        """
        self.game_street = GameStreet.RIVER

        # Burn a card if requested
        if burn_card:
            self.deck.deal_cards(1)

        # Deal river card if needed
        for board in self.boards:
            # Count existing cards (approximately)
            if (
                board.cards > 0 and len(board.community_cards) == 4
            ):  # Has turn but not river
                board.add_cards(self.deck.deal_cards(1))

        # Reset betting round for new street
        self._reset_betting_round()

        # Board dealing tracked only via external process_game_action

    def advance_to_showdown(self) -> None:
        """Advance the game to the showdown street."""
        self.game_street = GameStreet.SHOWDOWN

    def _get_additional_state(self) -> Dict[str, Any]:
        """Get additional state specific to the game variant.

        Subclasses can override this to include game-specific state that needs
        to be saved for undo functionality.

        Returns:
            Dict[str, Any]: Additional state data
        """
        return {}

    def _restore_additional_state(self, additional_state: Dict[str, Any]) -> None:
        """Restore additional state specific to the game variant.

        Subclasses can override this to restore game-specific state.

        Args:
            additional_state: The additional state data to restore
        """
        raise NotImplementedError(
            "Subclasses must implement _restore_additional_state to handle game-specific logic."
        )

    def _save_state_snapshot(self) -> None:
        """Save a snapshot of the current game state for undo functionality."""
        # Extract player actions from game_actions for compatibility
        actions_data = []
        for game_action in self.game_actions:
            if (
                game_action.action_type == GameActionType.ACCEPT_PLAYER_ACTION
                and game_action.details
            ):
                actions_data.append(
                    {
                        "player_code": game_action.details.get("player", "unknown"),
                        "action_type": game_action.details.get(
                            "action_type", "unknown"
                        ),
                        "stack": game_action.details.get("amount", 0),
                    }
                )

        snapshot = {
            "actions_data": actions_data,
            "actions": actions_data,  # Alias for compatibility
            "pots": deepcopy(self.pots),
            "pot_state": deepcopy(self.pots),  # Alias for compatibility
            "player_contributions": {
                getattr(player, "code", str(player)): contribution
                for player, contribution in self.player_contributions.items()
            },
            "players_acted_this_round": {
                getattr(player, "code", str(player))
                for player in self.players_acted_this_round
            },
            "game_street": self.game_street,
            "player_to_act": self.player_to_act,
            "player_to_act_code": (
                getattr(self.player_to_act, "code", None)
                if self.player_to_act
                else None
            ),
            "player_stacks": {
                getattr(player, "code", str(player)): player.stack
                for player in self.table.players
            },
            "player_statuses": {
                getattr(player, "code", str(player)): player.status
                for player in self.table.players
            },
            "player_states": {
                getattr(player, "code", str(player)): {
                    "stack": player.stack,
                    "status": player.status,
                }
                for player in self.table.players
            },  # Alias for compatibility
            "boards": deepcopy(self.boards),
            "deck_state": deepcopy(self.deck),
            "game_actions": deepcopy(self.game_actions),
            "actions_cache": self._actions_cache.copy(),  # Store copy, not reference
            "actions_cache_version": self._actions_cache_version,
            "additional_state": self._get_additional_state(),
        }
        self.state_snapshot = snapshot
        self._previous_state = snapshot

    def _restore_state_snapshot(self) -> bool:
        """Restore the game state from the saved snapshot.

        Returns:
            bool: True if state was successfully restored, False if no snapshot exists
        """
        if not self._previous_state:
            return False

        try:
            # Check for required fields first
            required_fields = [
                "actions_data",
                "pots",
                "player_contributions",
                "game_street",
                "player_to_act_code",
                "player_stacks",
                "player_statuses",
                "boards",
                "deck_state",
            ]
            for field in required_fields:
                if field not in self._previous_state:
                    return False

            # Restore game_actions from snapshot
            if "game_actions" in self._previous_state:
                self.game_actions = deepcopy(self._previous_state["game_actions"])

            # Restore actions cache from snapshot
            if "actions_cache" in self._previous_state:
                self._actions_cache = self._previous_state[
                    "actions_cache"
                ].copy()  # Restore copy, not reference
            if "actions_cache_version" in self._previous_state:
                self._actions_cache_version = self._previous_state[
                    "actions_cache_version"
                ]

            self.pots = deepcopy(self._previous_state["pots"])

            # Restore player contributions by mapping codes back to player objects
            self.player_contributions = {}
            for player in self.table.players:
                player_code = getattr(player, "code", str(player))
                if player_code in self._previous_state["player_contributions"]:
                    self.player_contributions[player] = self._previous_state[
                        "player_contributions"
                    ][player_code]

            # Restore players who acted this round
            self.players_acted_this_round = set()
            if "players_acted_this_round" in self._previous_state:
                for player in self.table.players:
                    player_code = getattr(player, "code", str(player))
                    if player_code in self._previous_state["players_acted_this_round"]:
                        self.players_acted_this_round.add(player)

            self.game_street = self._previous_state["game_street"]

            # Restore player to act
            if self._previous_state["player_to_act_code"]:
                for player in self.table.players:
                    player_code = getattr(player, "code", str(player))
                    if player_code == self._previous_state["player_to_act_code"]:
                        self.player_to_act = player
                        break

            self.boards = deepcopy(self._previous_state["boards"])
            self.deck = deepcopy(self._previous_state["deck_state"])

            # Restore game actions if present
            if "game_actions" in self._previous_state:
                self.game_actions = deepcopy(self._previous_state["game_actions"])

            # Restore player stacks and statuses
            for player in self.table.players:
                player_code = getattr(player, "code", str(player))
                if player_code in self._previous_state["player_stacks"]:
                    player.stack = self._previous_state["player_stacks"][player_code]
                if player_code in self._previous_state["player_statuses"]:
                    player.status = self._previous_state["player_statuses"][player_code]

            # Restore additional game-specific state
            if "additional_state" in self._previous_state:
                self._restore_additional_state(self._previous_state["additional_state"])

            return True
        except (KeyError, TypeError, AttributeError):
            return False

    def can_undo(self) -> bool:
        """Check if an undo operation is possible.

        Returns:
            bool: True if there is a saved state that can be restored, False otherwise
        """
        # Extract player actions from game_actions
        player_actions = [
            ga.details.get("player_action")
            for ga in self.game_actions
            if ga.action_type == GameActionType.ACCEPT_PLAYER_ACTION
            and ga.details
            and "player_action" in ga.details
        ]

        if self._previous_state is None or len(player_actions) == 0:
            return False

        # Check if snapshot has required fields
        required_fields = [
            "game_street",
            "actions_data",
            "pots",
            "player_contributions",
        ]
        for field in required_fields:
            if field not in self._previous_state:
                return False

        # Check if street has changed since the snapshot was taken
        # We need to detect if the street was manually changed after the snapshot
        snapshot_street = self._previous_state["game_street"]
        current_street = self.game_street

        if snapshot_street != current_street:
            # Street changed - we need to determine if this was manual or auto-progression

            # If the last action in our history would have caused auto-progression,
            # and the current street is what we'd expect from auto-progression, allow undo
            if len(player_actions) > 0:
                last_action = player_actions[-1]

                # Check if the street change matches what auto-progression would do
                expected_street_after_auto_progression = (
                    self._get_expected_street_after_action(
                        last_action, snapshot_street, current_street
                    )
                )

                if current_street == expected_street_after_auto_progression:
                    # This looks like natural auto-progression, allow undo
                    return True
                else:
                    # Street changed to something unexpected, likely manual change
                    return False
            else:
                # No actions but street changed - definitely manual
                return False

        return True

    def _get_expected_street_after_action(
        self,
        action: PlayerAction,
        original_street: GameStreet,
        current_street: GameStreet,
    ) -> GameStreet:
        """Determine what street the game should be in after auto-progression from the given action."""
        # This is a simplified check - in reality, auto-progression logic is complex
        # But for undo purposes, we mainly care about detecting manual street changes

        # Check if only one player remains (or would remain after this action)
        active_players = [
            p
            for p in self.table.players
            if p.status not in [PlayerStatus.FOLDED, PlayerStatus.SITOUT]
        ]

        # Special case: if there's only one player in the game, game should end
        if len(self.table.players) == 1:
            return GameStreet.SHOWDOWN

        # If action caused only one player to remain, should go to SHOWDOWN
        if action.action_type == PlayerActionType.FOLD:
            if len(active_players) <= 1:
                return GameStreet.SHOWDOWN

        # If all players went all-in, should go to SHOWDOWN
        all_in_or_folded = all(
            p.status in [PlayerStatus.ALLIN, PlayerStatus.FOLDED, PlayerStatus.SITOUT]
            for p in self.table.players
        )

        if all_in_or_folded and len(active_players) > 1:
            return GameStreet.SHOWDOWN

        # Check for betting round completion that would cause street progression
        # This is more complex because we need to simulate the betting round state
        if action.action_type in [
            PlayerActionType.CALL,
            PlayerActionType.CHECK,
            PlayerActionType.ALLIN,
        ] and (
            (
                original_street == GameStreet.PRE_FLOP
                and current_street == GameStreet.FLOP
            )
            or (
                original_street == GameStreet.FLOP and current_street == GameStreet.TURN
            )
            or (
                original_street == GameStreet.TURN
                and current_street == GameStreet.RIVER
            )
            or (
                original_street == GameStreet.RIVER
                and current_street == GameStreet.SHOWDOWN
            )
        ):
            # This could be natural street progression due to betting round completion
            # We'll assume it's natural if the action is a call, check, or all-in
            return current_street

        # No auto-progression expected
        return original_street

    def _would_betting_round_be_complete_after_action(
        self, action: PlayerAction
    ) -> bool:
        """Check if the betting round would be complete after this action."""
        # Get all players who can still act (not folded, all-in, or sitting out)
        active_players = [
            p for p in self.table.players if p.status == PlayerStatus.INGAME
        ]

        if len(active_players) <= 1:
            return True  # Only 0-1 active players, no more betting needed

        # Simulate the action being processed
        # Check if all active players would have acted in this betting round
        players_who_would_have_acted = self.players_acted_this_round.copy()
        players_who_would_have_acted.add(action.player)

        active_players_who_would_act = players_who_would_have_acted.intersection(
            set(active_players)
        )

        if len(active_players_who_would_act) < len(active_players):
            return False  # Not all active players would have acted yet

        # All active players would have acted, check if contributions would be equal
        # Simulate the contribution after this action
        simulated_contributions = dict(self.player_contributions)
        if action.player not in simulated_contributions:
            simulated_contributions[action.player] = 0.0

        if action.action_type in [
            PlayerActionType.BET,
            PlayerActionType.CALL,
            PlayerActionType.RAISE,
            PlayerActionType.ALLIN,
        ]:
            simulated_contributions[action.player] += action.stack

        active_contributions = [
            simulated_contributions.get(p, 0.0) for p in active_players
        ]
        contributions_equal = len(set(active_contributions)) <= 1

        return contributions_equal

    def undo_last_action(self) -> bool:
        """Undo the last action and restore the previous game state.

        Returns:
            bool: True if the undo was successful, False if no undo is possible
        """
        if not self.can_undo():
            return False

        success = self._restore_state_snapshot()
        if success:
            # Clear the snapshot to prevent multiple undos
            self.state_snapshot = None
            self._previous_state = None
        return success

    def is_hand_complete(self) -> bool:
        """Check if the current hand is complete (only one active player or showdown reached).

        Returns:
            bool: True if hand is complete, False otherwise
        """
        active_players = [
            p
            for p in self.table.players
            if p.status not in [PlayerStatus.FOLDED, PlayerStatus.SITOUT]
        ]
        return len(active_players) <= 1 or self.game_street == GameStreet.SHOWDOWN

    def get_winners(self) -> List[TablePlayer]:
        """Get the winners of the current hand.

        Returns:
            List[TablePlayer]: List of winning players
        """
        active_players = [
            p
            for p in self.table.players
            if p.status not in [PlayerStatus.FOLDED, PlayerStatus.SITOUT]
        ]

        if len(active_players) == 1:
            # Only one player left - they win by default
            winners = active_players
        elif len(active_players) == 0:
            # No active players (shouldn't happen in normal gameplay)
            winners = []
        else:
            # Multiple players - need hand evaluation
            # For now, return all active players (this would need proper hand evaluation)
            winners = active_players

        # Winner determination happens automatically - no external tracking needed

        return winners

    def _is_betting_round_complete(self) -> bool:
        """Check if the current betting round is complete.

        Returns:
            bool: True if betting round is complete, False otherwise
        """
        # Get all players who can still act (not folded, all-in, or sitting out)
        active_players = [
            p for p in self.table.players if p.status == PlayerStatus.INGAME
        ]

        if len(active_players) == 0:
            return True  # No active players, betting round is complete

        if len(active_players) == 1:
            # Special case: only one active player left
            # Check if there's a current bet that player needs to match
            current_bet = max(self.player_contributions.values()) if self.player_contributions else 0.0
            if current_bet == 0.0:
                return True  # No bet to match, round is complete

            # Check if the active player has matched the current bet
            active_player = active_players[0]
            player_contribution = self.player_contributions.get(active_player, 0.0)
            if player_contribution >= current_bet:
                return True  # Player has matched the bet, round is complete
            else:
                return False  # Player still needs to match the bet

        # Check if all active players have acted in this betting round
        active_players_who_acted = self.players_acted_this_round.intersection(
            set(active_players)
        )

        if len(active_players_who_acted) < len(active_players):
            return False  # Not all active players have acted yet

        # All active players have acted, now check if they've matched the current bet
        # Current bet is the highest contribution from ALL players (including ALLIN)
        current_bet = max(self.player_contributions.values()) if self.player_contributions else 0.0

        # Check if all active players have either matched the current bet or gone all-in
        for player in active_players:
            player_contribution = self.player_contributions.get(player, 0.0)
            if player_contribution < current_bet:
                # Player hasn't matched the current bet yet
                return False

        return True

    def can_advance_street(self) -> bool:
        """Check if the game can advance to the next street.

        Returns:
            bool: True if can advance street, False otherwise
        """
        return self._is_betting_round_complete()

    def get_result(self) -> List[Dict[str, Any]]:
        """Return a list of dictionaries containing the result of the game.

        Each dictionary contains the key of a pot, the key of a board, and a list
        of the winners for that board. The winners are represented as a list of
        player keys.

        Returns:
            A list of dictionaries with the game result.
        """
        result: List[Dict[str, Any]] = []
        for pot in self.pots:
            boards_count = len(self.boards)
            players: List[TablePlayer] = [
                player
                for player in pot.players
                if player.status in [PlayerStatus.INGAME, PlayerStatus.ALLIN]
            ]
            for board in self.boards:
                winning_players = get_winners(board.cards, players)
                winners = [
                    f"{player.code} - {extract_cards(player.hand.cards)} - {player.hand.type_name}"
                    for player in winning_players
                ]
                number_of_winners = len(winners)
                share_per_player = 0.0
                if pot.stack > 0 and number_of_winners > 0:
                    share_per_player = (pot.stack / boards_count) / number_of_winners
                result.append(
                    {
                        "pot": pot.key,
                        "board": board.key,
                        "share_per_player": share_per_player,
                        "winners": winners,
                    }
                )
        return result

    def distribute_pots(self) -> List[Dict[str, Any]]:
        """
        Distribute pot winnings to players and return the results.

        This method gets the game results and automatically awards winnings
        to players by updating their stack amounts. Should be called after
        hand completion to finalize the game.

        Returns:
            List[Dict[str, Any]]: Same format as get_result() but with actual
            money distribution having occurred.
        """
        results = self.get_result()
        distributions = {}
        total_distributed = 0

        for result in results:
            share_per_player = result["share_per_player"]
            winners = result["winners"]

            # Extract winner player codes from result strings
            # Format: "PlayerName - [cards] - hand_type"
            for winner_string in winners:
                player_code = winner_string.split(" - ")[0]

                # Find the player and award winnings
                for player in self.table.players:
                    if player.code == player_code:
                        player.stack += share_per_player
                        if player_code not in distributions:
                            distributions[player_code] = 0
                        distributions[player_code] += share_per_player
                        total_distributed += share_per_player
                        break

        # Pot distribution happens automatically - no external tracking needed

        return results

    def end_game(self) -> None:
        """End the current game and prepare for next hand.

        This method should be called after pot distribution to mark
        the end of the current hand and prepare for the next hand.
        """
        # Game ending happens automatically - no external tracking needed

    def process_game_action(
        self,
        game_action_type: GameActionType,
        action_details: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Process a game action triggered by external applications.

        This is the main interface for external applications to interact with the game.
        It handles the 4 external game actions and routes them to appropriate internal methods.

        Args:
            game_action_type: The type of game action to process
            action_details: Additional details for the action (can be None)

        Returns:
            bool: True if action was processed successfully, False otherwise
        """
        try:
            if game_action_type == GameActionType.ACCEPT_BLINDS:
                return self._process_accept_blinds(action_details)

            elif game_action_type == GameActionType.DEAL_HOLE_CARDS:
                return self._process_deal_hole_cards(action_details)

            elif game_action_type == GameActionType.ACCEPT_PLAYER_ACTION:
                return self._process_accept_player_action(action_details)

            elif game_action_type == GameActionType.DEAL_BOARD:
                return self._process_deal_board(action_details)

            else:
                return False

        except (ValueError, TypeError):
            return False

    def _process_accept_blinds(self, action_details: Optional[Dict[str, Any]]) -> bool:
        """Process ACCEPT_BLINDS action.

        For regular games:
            action_details = None

        For bomb pot games:
            action_details = {
                "participating_players": []  # List of player codes who are participating
            }
        """
        # Validate action_details format
        if action_details is not None:
            if not isinstance(action_details, dict):
                return False
            if "participating_players" in action_details:
                if not isinstance(action_details["participating_players"], list):
                    return False
                # Validate that all participating players exist
                player_codes = [getattr(p, 'code', str(p)) for p in self.table.players]
                for participant in action_details["participating_players"]:
                    if participant not in player_codes:
                        return False

        # Track the game action
        self._track_game_action(GameActionType.ACCEPT_BLINDS, action_details)

        # For regular games, just call post_blinds()
        if action_details is None:
            if hasattr(self, "post_blinds"):
                self.post_blinds()
                return True

        # For bomb pot games with participating players
        elif "participating_players" in action_details:
            if hasattr(self, "post_bomb_amounts"):
                self.post_bomb_amounts()
                return True

        return False

    def _process_deal_hole_cards(
        self, action_details: Optional[Dict[str, Any]]
    ) -> bool:
        """Process DEAL_HOLE_CARDS action.

        For random cards:
            action_details = None

        For specific cards:
            action_details = {
                "player_cards": [("A♥", "K♣"), ("K♦", "Q♥")]
            }
        """
        # Validate action_details format
        if action_details is not None:
            if not isinstance(action_details, dict):
                return False
            if "player_cards" in action_details:
                if not isinstance(action_details["player_cards"], list):
                    return False
                # Validate each player's cards
                for player_cards in action_details["player_cards"]:
                    if not isinstance(player_cards, (list, tuple)):
                        return False
                    # Each player should have cards (tuples of strings)
                    for card in player_cards:
                        if not isinstance(card, str):
                            return False

        # Track the game action
        self._track_game_action(GameActionType.DEAL_HOLE_CARDS, action_details)

        if action_details is None:
            # Deal random cards
            self.deal_hole_cards()
            return True

        elif "player_cards" in action_details:
            # Deal specific cards
            player_cards = action_details["player_cards"]
            # Convert string cards to int masks
            converted_cards = []
            for card_tuple in player_cards:
                # Pass all cards for this player at once to get the combined mask
                hole_cards_mask = get_card_keys_from_codes(list(card_tuple))
                converted_cards.append(hole_cards_mask)

            self.deal_hole_cards(converted_cards)
            return True

        return False

    def _process_accept_player_action(
        self, action_details: Optional[Dict[str, Any]]
    ) -> bool:
        """Process ACCEPT_PLAYER_ACTION action.

        Expected format:
            action_details = {
                "player_action": PlayerAction(player, PlayerActionType.BET, 30)
            }
        """
        # Validate action_details format
        if action_details is None:
            return False
        if not isinstance(action_details, dict):
            return False
        if "player_action" not in action_details:
            return False

        player_action = action_details["player_action"]

        # Validate that player_action is a PlayerAction instance
        if not isinstance(player_action, PlayerAction):
            return False

        # Validate that the player exists in the game
        player_codes = [getattr(p, 'code', str(p)) for p in self.table.players]
        player_code = getattr(player_action.player, 'code', str(player_action.player))
        if player_code not in player_codes:
            return False

        # Track the game action
        self._track_game_action(
            GameActionType.ACCEPT_PLAYER_ACTION,
            {
                "player": getattr(
                    player_action.player, "code", str(player_action.player)
                ),
                "action_type": player_action.action_type.name,
                "amount": player_action.stack,
            },
        )

        return self.register_action(player_action)

    def _process_deal_board(self, action_details: Optional[Dict[str, Any]]) -> bool:
        """Process DEAL_BOARD action.

        For random cards:
            action_details = None

        For specific cards:
            action_details = {
                "board_cards": ["A♥"]
            }
        """
        # Validate action_details format
        if action_details is not None:
            if not isinstance(action_details, dict):
                return False
            if "board_cards" in action_details:
                if not isinstance(action_details["board_cards"], list):
                    return False
                # Validate each card is a string
                for card in action_details["board_cards"]:
                    if not isinstance(card, str):
                        return False

        # Track the game action
        self._track_game_action(GameActionType.DEAL_BOARD, action_details)

        if action_details is None:
            # Deal random cards based on current street
            if self.game_street == GameStreet.PRE_FLOP:
                self.advance_to_flop()
            elif self.game_street == GameStreet.FLOP:
                self.advance_to_turn()
            elif self.game_street == GameStreet.TURN:
                self.advance_to_river()
            return True

        elif "board_cards" in action_details:
            # Deal specific cards - this would need more implementation
            # For now, just advance to next street with random cards
            if self.game_street == GameStreet.PRE_FLOP:
                self.advance_to_flop()
            elif self.game_street == GameStreet.FLOP:
                self.advance_to_turn()
            elif self.game_street == GameStreet.TURN:
                self.advance_to_river()
            return True

        return False

    def add_boards_during_game(self, total_boards: int) -> None:
        """
        Add additional boards to the current game during play.

        This allows players to add boards at any point during the hand. Already dealt
        community cards are shared across all boards, while future cards are dealt
        separately for each board.

        Args:
            total_boards: Total number of boards to play (including existing boards)

        Raises:
            ValueError: If total_boards is invalid or timing is inappropriate
            RuntimeError: If game state doesn't allow adding boards
        """
        # Validation
        if total_boards <= 0:
            raise ValueError("Total boards must be positive")

        if total_boards <= len(self.boards):
            raise ValueError(
                f"Total boards ({total_boards}) must be greater than current boards ({len(self.boards)})"
            )

        if self.is_hand_complete():
            raise RuntimeError("Cannot add boards after hand is complete")

        # Check if there are multiple active players
        active_players = [
            p
            for p in self.table.players
            if p.status in [PlayerStatus.INGAME, PlayerStatus.ALLIN]
        ]
        if len(active_players) < 2:
            raise RuntimeError("Cannot add boards with fewer than 2 active players")

        # Calculate how many new boards to add
        boards_to_add = total_boards - len(self.boards)

        # Store current community cards from the first board
        current_community_cards = self.boards[0].cards if self.boards else 0
        current_community_card_list = (
            self.boards[0].community_cards.copy() if self.boards else []
        )

        # Add new boards
        for _ in range(boards_to_add):
            self._add_board_with_current_cards(
                current_community_cards, current_community_card_list.copy()
            )

        # Note: We do NOT deal additional cards here
        # Additional cards (turn, river) will be dealt by the normal game progression
        # when advance_to_turn() and advance_to_river() are called

        # Update pot structure for multiple boards if needed
        self._update_pots_for_multiple_boards()

    def _add_board_with_current_cards(
        self, cards: int, community_card_list: List[int]
    ) -> None:
        """
        Add a new board and copy the current community cards to it.

        Args:
            cards: Bitmask of current community cards
            community_card_list: List of individual community card keys
        """
        board_id = self.board_count + 1
        board = Board(board_id)

        # Copy current community cards to the new board
        if cards != 0:
            board.cards = cards
            board.community_cards = community_card_list.copy()
            # Update board texture for current cards
            board.texture = BoardTexture(cards)

        # Copy players from existing boards
        if self.boards:
            for existing_player in self.boards[0].players:
                # Create a copy of the board player for the new board
                # BoardPlayer inherits from TablePlayer, so we can convert back
                new_board_player = existing_player.to_board_player()
                if hasattr(existing_player, "hole_cards"):
                    new_board_player.set_hole_cards(existing_player.hole_cards)
                board.players.append(new_board_player)

        self.boards.append(board)
        self.board_count += 1

    def _deal_remaining_cards_to_boards(self) -> None:
        """
        Deal remaining community cards separately to each board based on current street.

        Cards already dealt are shared across all boards.
        Future cards are dealt separately to each board.
        """
        # During PRE_FLOP, no community cards should be dealt yet
        # Community cards are dealt when advancing to flop/turn/river
        if self.game_street == GameStreet.PRE_FLOP:
            return

        # For other streets, deal remaining cards for boards that need them
        cards_needed_per_board = 0

        if self.game_street == GameStreet.FLOP:
            cards_needed_per_board = 2  # Turn and river
        elif self.game_street == GameStreet.TURN:
            cards_needed_per_board = 1  # River only
        elif self.game_street == GameStreet.RIVER:
            cards_needed_per_board = 0  # No more cards needed

        # Deal cards separately to each board that needs them
        # But only deal the immediate future cards, not all remaining cards
        if cards_needed_per_board > 0:
            for board in self.boards:
                # Check how many cards this board already has
                current_card_count = len(board.community_cards)

                # For multi-boarding, we don't deal all future cards immediately
                # We only deal what's needed for the current street progression
                # The normal game progression will handle dealing turn/river cards
                # when those streets are reached

                # Don't deal any additional cards here - let normal game progression handle it
                # This method should only be used for very specific cases where we need
                # to ensure boards have the minimum cards for their current state
                pass

    def _update_pots_for_multiple_boards(self) -> None:
        """
        Update pot structure to handle multiple boards.

        With multiple boards, each pot will be split across all boards proportionally.
        This doesn't change the pot amounts, but affects how results are calculated.
        """
        # The pot splitting logic is handled in get_result() method
        # which already divides pot amounts by the number of boards
        # No additional pot structure changes needed here
        raise NotImplementedError(
            "Pot splitting for multiple boards is handled in get_result() method."
        )
