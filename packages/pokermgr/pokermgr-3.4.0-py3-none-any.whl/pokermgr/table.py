"""Table"""
from collections import deque
from pokermgr.player import TablePlayer


class Table:
    """
    A class representing a poker table where the game is played.

    The Table class manages the state of the poker table, including maintaining the list of
    players, enforcing table limits, and handling player rotations.

    Attributes:
        code (str): A unique identifier for the table.
        max_players (int): Maximum number of players allowed at the table. Defaults to 9.
        players (deque[TablePlayer]): A double-ended queue of players at the table.
    """
    def __init__(self, code: str, players: deque[TablePlayer], max_players: int = 9) -> None:
        """
        Initialize the table with the given parameters.

        Args:
            code: A unique identifier for the table.
            players: Initial list of players at the table.
            max_players: Maximum number of players allowed at the table. Defaults to 9.

        Note:
            The players are stored in a deque to facilitate easy rotation.
        """
        self.code = code
        self.max_players = max_players
        self.players = players

    def player_exists(self, player: TablePlayer) -> bool:
        """
        Check if a player is already at the table.

        Args:
            player: The TablePlayer instance to check.

        Returns:
            bool: True if the player is at the table, False otherwise.
        """
        return player in self.players

    def add_player(self, player: TablePlayer) -> None:
        """
        Add a player to the table.

        Args:
            player: The TablePlayer instance to add to the table.

        Raises:
            ValueError: If the table is already at maximum capacity.
        """
        if len(self.players) >= self.max_players:
            raise ValueError("Table is full")
        if self.player_exists(player):
            raise ValueError("Player is already at the table")
        self.players.append(player)

    def remove_player(self, player: TablePlayer) -> None:
        """
        Remove a player from the table.

        Args:
            player: The TablePlayer instance to remove from the table.

        Raises:
            ValueError: If the specified player is not found at the table.
        """
        if not self.player_exists(player):
            raise ValueError("Player is not at the table")
        self.players.remove(player)

    def move_players(self) -> None:
        """
        Rotate player positions at the table.

        This method rotates the players' positions by moving the first player to the end
        of the queue. This is typically used for changing dealer/button positions.
        """
        self.players.rotate()

    def __str__(self) -> str:
        """
        Return a string representation of the table.

        Returns:
            str: The table's code as its string representation.
        """
        return f"{self.code}"

    def __repr__(self) -> str:
        """
        Return an unambiguous string representation of the table.

        Returns:
            str: A string that can be used to recreate the table object.
        """
        return f"{self.code}"
