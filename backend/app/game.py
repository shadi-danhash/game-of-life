from typing import Set, Tuple

Point = Tuple[int, int]

class GameBase:
    """
    Base class for simulating the Conway's Game of Life.
    The grid is represented as a set of active cell coordinates.
    """
    def __init__(self, state: Set[Point] = None):
        """
        Initialize the game with an optional initial state.

        Args:
            state (Set[Point], optional): Set of active cell coordinates. Defaults to empty set.
        """
        self._state: Set[Point] = state or set()
        self._directions: Tuple[Point, ...] = tuple(
            (dx, dy) for dx in range(-1, 2) for dy in range(-1, 2) if (dx, dy) != (0, 0)
        )

    def _get_new_value(self, current_value: bool, active_neighbors: int) -> bool:
        """
        Computes the next value of a cell based on its current state and number of active neighbors.

        Args:
            current_value (bool): Whether the cell is currently active.
            active_neighbors (int): Number of active neighboring cells.

        Returns:
            bool: True if the cell will be active in the next state, False otherwise.
        """
        return active_neighbors == 3 or (current_value and active_neighbors == 2)

    def get_current_state(self) -> Set[Point]:
        """
        Returns a copy of the current active cells state.

        Returns:
            Set[Point]: A copy of the current state.
        """
        return self._state.copy()

    def _get_neighbors(self, point: Point, state: Set[Point]) -> Tuple[Set[Point], Set[Point]]:
        """
        Computes the active and dead neighbors of a given cell.

        Args:
            point (Point): The cell coordinate (x, y).
            state (Set[Point]): The set of currently active cells.

        Returns:
            Tuple[Set[Point], Set[Point]]: A tuple containing sets of active and dead neighbors.
        """
        dead: Set[Point] = set()
        active: Set[Point] = set()
        x, y = point
        for i, j in self._directions:
            neighbor = (x + i, y + j)
            if neighbor in state:
                active.add(neighbor)
            else:
                dead.add(neighbor)
        return active, dead

    def _next_state(self, state: Set[Point]) -> Set[Point]:
        """
        Computes the next state of the game based on the current state.

        Args:
            state (Set[Point]): The current set of active cells.

        Returns:
            Set[Point]: The next set of active cells.
        """
        next_state: Set[Point] = set()
        deads: Set[Point] = set()

        for active in state:
            active_neighbors, dead_neighbors = self._get_neighbors(active, state)
            if self._get_new_value(True, len(active_neighbors)):
                next_state.add(active)
            deads.update(dead_neighbors)

        for dead in deads:
            active_neighbors, _ = self._get_neighbors(dead, state)
            if self._get_new_value(False, len(active_neighbors)):
                next_state.add(dead)

        return next_state

    def next(self) -> Tuple[Set[Point], Set[Point]]:
        """
        Advances the game state by one step and returns only the changes.

        Returns:
            Tuple[Set[Point], Set[Point]]: A tuple of (activated cells, deactivated cells).
        """
        old_state = self.get_current_state()
        self._state = self._next_state(state=old_state)
        active = self._state - old_state
        dead = old_state - self._state
        return active, dead
    
    def toggle_point(self, point: Point) -> bool:
        """
        This function switches the status of the point.

        Args:
            point (Point): The point to toggle.

        Returns:
            bool: The new status of the point.
        """
        if point in self._state:
            self._state.remove(point)
            return False
        self._state.add(point)
        return True
