# Copyright (C) 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: Apache-2.0

#
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# ©2026, ANSYS Inc. Unauthorized use, distribution or duplication is prohibited.

"""Conway's Game of Life - Core Business Logic.

This module implements the core logic for Conway's Game of Life simulation,
including the game engine, pattern library, and simulation controller.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

import numpy as np


class PatternCategory(Enum):
    """Categories for Game of Life patterns.

    Only evolving patterns are catalogued: still lives are excluded on purpose
    so that every selectable pattern animates when the simulation runs.
    """

    OSCILLATOR = "oscillator"
    SPACESHIP = "spaceship"
    RANDOM = "random"


@dataclass
class Pattern:
    """Definition of a Game of Life pattern.

    Attributes
    ----------
    name : str
        Display name of the pattern.
    category : PatternCategory
        Category of the pattern.
    description : str
        Description of the pattern's behavior.
    pattern : np.ndarray
        2D array representing the pattern (1=alive, 0=dead).
    period : Optional[int]
        Period for oscillators (None for non-periodic patterns).
    """

    name: str
    category: PatternCategory
    description: str
    pattern: np.ndarray
    period: Optional[int] = None


class PatternLibrary:
    """Library of predefined evolving Game of Life patterns.

    Holds oscillators and spaceships only. Still lives are intentionally not
    offered, since a stable pattern never changes once the simulation starts.
    """

    def __init__(self):
        """Initialize the pattern library with predefined patterns."""
        self._patterns: dict[str, Pattern] = {}
        self._initialize_patterns()

    def _initialize_patterns(self) -> None:
        """Initialize all predefined patterns."""
        # Oscillators
        self._patterns["blinker"] = Pattern(
            name="Blinker",
            category=PatternCategory.OSCILLATOR,
            description="A period-2 oscillator (horizontal/vertical line)",
            pattern=np.array([[1, 1, 1]], dtype=np.int8),
            period=2,
        )

        self._patterns["toad"] = Pattern(
            name="Toad",
            category=PatternCategory.OSCILLATOR,
            description="A period-2 oscillator",
            pattern=np.array([[0, 1, 1, 1], [1, 1, 1, 0]], dtype=np.int8),
            period=2,
        )

        self._patterns["beacon"] = Pattern(
            name="Beacon",
            category=PatternCategory.OSCILLATOR,
            description="A period-2 oscillator",
            pattern=np.array(
                [[1, 1, 0, 0], [1, 1, 0, 0], [0, 0, 1, 1], [0, 0, 1, 1]],
                dtype=np.int8,
            ),
            period=2,
        )

        self._patterns["pulsar"] = Pattern(
            name="Pulsar",
            category=PatternCategory.OSCILLATOR,
            description="A period-3 oscillator",
            pattern=np.array(
                [
                    [0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1],
                    [1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1],
                    [1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1],
                    [0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0],
                    [1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1],
                    [1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1],
                    [1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0],
                ],
                dtype=np.int8,
            ),
            period=3,
        )

        # Spaceships
        self._patterns["glider"] = Pattern(
            name="Glider",
            category=PatternCategory.SPACESHIP,
            description="A pattern that moves diagonally across the grid",
            pattern=np.array([[0, 1, 0], [0, 0, 1], [1, 1, 1]], dtype=np.int8),
        )

        self._patterns["lwss"] = Pattern(
            name="Lightweight Spaceship (LWSS)",
            category=PatternCategory.SPACESHIP,
            description="A spaceship that moves horizontally",
            pattern=np.array(
                [[0, 1, 0, 0, 1], [1, 0, 0, 0, 0], [1, 0, 0, 0, 1], [1, 1, 1, 1, 0]],
                dtype=np.int8,
            ),
        )

        self._patterns["gosper_glider_gun"] = Pattern(
            name="Gosper Glider Gun",
            category=PatternCategory.SPACESHIP,
            description="A pattern that produces gliders",
            pattern=np.array(
                [
                    # fmt: off
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                     0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                     0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0,
                     0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0,
                     0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
                    [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0,
                     0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 1,
                     0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0,
                     0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0,
                     0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0,
                     0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    # fmt: on
                ],
                dtype=np.int8,
            ),
        )

    def get_pattern_list(self) -> list[str]:
        """Get list of available pattern names.

        Returns
        -------
        list[str]
            List of pattern identifiers.
        """
        return list(self._patterns.keys())

    def get_pattern(self, pattern_name: str) -> Pattern:
        """Get a pattern by name.

        Parameters
        ----------
        pattern_name : str
            Name of the pattern to retrieve.

        Returns
        -------
        Pattern
            The requested pattern.

        Raises
        ------
        KeyError
            If the pattern name is not found.
        """
        if pattern_name not in self._patterns:
            raise KeyError(f"Pattern '{pattern_name}' not found. " f"Available patterns: {self.get_pattern_list()}")
        return self._patterns[pattern_name]

    def get_patterns_by_category(self, category: PatternCategory) -> dict[str, Pattern]:
        """Get all patterns in a specific category.

        Parameters
        ----------
        category : PatternCategory
            The category to filter by.

        Returns
        -------
        dict[str, Pattern]
            Dictionary of patterns in the specified category.
        """
        return {name: pattern for name, pattern in self._patterns.items() if pattern.category == category}

    @staticmethod
    def place_pattern_on_grid(
        grid: np.ndarray,
        pattern: np.ndarray,
        position: Optional[tuple[int, int]] = None,
    ) -> np.ndarray:
        """Place a pattern on a grid at a specified position.

        Parameters
        ----------
        grid : np.ndarray
            The grid to place the pattern on.
        pattern : np.ndarray
            The pattern to place.
        position : Optional[tuple[int, int]]
            The (row, col) position to place the pattern's top-left corner.
            If None, the pattern is centered on the grid.

        Returns
        -------
        np.ndarray
            The grid with the pattern placed on it.
        """
        grid = grid.copy()
        pattern_rows, pattern_cols = pattern.shape
        grid_rows, grid_cols = grid.shape

        if position is None:
            # Center the pattern (may be negative if pattern is larger than grid)
            start_row = (grid_rows - pattern_rows) // 2
            start_col = (grid_cols - pattern_cols) // 2
        else:
            start_row, start_col = position

        # Intersection of the pattern's footprint with the grid.
        grid_start_row = max(start_row, 0)
        grid_start_col = max(start_col, 0)
        grid_end_row = min(start_row + pattern_rows, grid_rows)
        grid_end_col = min(start_col + pattern_cols, grid_cols)

        # Nothing to place if the pattern lies fully outside the grid.
        if grid_start_row >= grid_end_row or grid_start_col >= grid_end_col:
            return grid

        # Corresponding slice inside the pattern.
        pattern_start_row = grid_start_row - start_row
        pattern_start_col = grid_start_col - start_col
        pattern_end_row = grid_end_row - start_row
        pattern_end_col = grid_end_col - start_col

        grid[grid_start_row:grid_end_row, grid_start_col:grid_end_col] = pattern[
            pattern_start_row:pattern_end_row, pattern_start_col:pattern_end_col
        ]

        return grid


class GameOfLifeEngine:
    """Core engine for computing Game of Life generations."""

    @staticmethod
    def count_neighbors(grid: np.ndarray, row: int, col: int) -> int:
        """Count live neighbors for a cell at (row, col).

        Uses Moore neighborhood (8 surrounding cells).

        Parameters
        ----------
        grid : np.ndarray
            Current grid state.
        row : int
            Row index of the cell.
        col : int
            Column index of the cell.

        Returns
        -------
        int
            Count of live neighbors (0-8).
        """
        rows, cols = grid.shape
        count = 0

        # Check all 8 neighbors
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                # Skip the cell itself
                if dr == 0 and dc == 0:
                    continue

                neighbor_row = row + dr
                neighbor_col = col + dc

                # Check if neighbor is within bounds
                if 0 <= neighbor_row < rows and 0 <= neighbor_col < cols:
                    count += grid[neighbor_row, neighbor_col]

        return count

    @staticmethod
    def apply_rules(cell_state: int, neighbor_count: int) -> int:
        """Apply Conway's Game of Life rules to determine next cell state.

        Rules:
        - Any live cell with 2 or 3 live neighbors survives
        - Any dead cell with exactly 3 live neighbors becomes alive
        - All other cells die or stay dead

        Parameters
        ----------
        cell_state : int
            Current state of the cell (0=dead, 1=alive).
        neighbor_count : int
            Number of live neighbors.

        Returns
        -------
        int
            Next state of the cell (0=dead, 1=alive).
        """
        if cell_state == 1:
            # Cell is alive
            if neighbor_count in [2, 3]:
                return 1  # Survival
            else:
                return 0  # Death by underpopulation or overpopulation
        else:
            # Cell is dead
            if neighbor_count == 3:
                return 1  # Reproduction
            else:
                return 0  # Stay dead

    @classmethod
    def compute_next_generation(cls, current_grid: np.ndarray) -> np.ndarray:
        """Compute the next generation based on Conway's rules.

        This method uses vectorized operations for optimal performance.

        Parameters
        ----------
        current_grid : np.ndarray
            Current state of the grid.

        Returns
        -------
        np.ndarray
            New grid representing the next generation.
        """
        rows, cols = current_grid.shape
        next_grid = np.zeros_like(current_grid, dtype=np.int8)

        # Vectorized neighbor counting via the eight shifted views of the
        # zero-padded grid. Each shift represents one of the eight Moore
        # neighbours; the sum stays within int8 range (max value: 8).
        padded_grid = np.pad(current_grid, pad_width=1, mode="constant", constant_values=0)

        neighbor_counts = (
            padded_grid[0:rows, 0:cols]  # top-left
            + padded_grid[0:rows, 1 : cols + 1]  # top
            + padded_grid[0:rows, 2 : cols + 2]  # top-right
            + padded_grid[1 : rows + 1, 0:cols]  # left
            + padded_grid[1 : rows + 1, 2 : cols + 2]  # right
            + padded_grid[2 : rows + 2, 0:cols]  # bottom-left
            + padded_grid[2 : rows + 2, 1 : cols + 1]  # bottom
            + padded_grid[2 : rows + 2, 2 : cols + 2]  # bottom-right
        )

        # Apply rules vectorized
        # Live cells with 2 or 3 neighbors survive
        survive = (current_grid == 1) & ((neighbor_counts == 2) | (neighbor_counts == 3))
        # Dead cells with 3 neighbors become alive
        birth = (current_grid == 0) & (neighbor_counts == 3)

        next_grid[survive | birth] = 1

        return next_grid

    @classmethod
    def initialize_grid(
        cls,
        pattern_name: str,
        grid_size: tuple[int, int],
        pattern_library: PatternLibrary,
    ) -> np.ndarray:
        """Initialize a grid with a predefined pattern.

        Parameters
        ----------
        pattern_name : str
            Name of the pattern to load.
        grid_size : tuple[int, int]
            Tuple of (rows, cols).
        pattern_library : PatternLibrary
            The pattern library to load patterns from.

        Returns
        -------
        np.ndarray
            2D numpy array representing the initial grid state.
        """
        grid = np.zeros(grid_size, dtype=np.int8)

        if pattern_name == "random":
            # Generate random pattern with ~30% live cells
            grid = np.random.choice([0, 1], size=grid_size, p=[0.7, 0.3]).astype(np.int8)
        else:
            pattern = pattern_library.get_pattern(pattern_name)
            grid = pattern_library.place_pattern_on_grid(grid, pattern.pattern)

        return grid


@dataclass
class SimulationState:
    """State of the Game of Life simulation.

    Attributes
    ----------
    grid : np.ndarray
        Current grid state.
    generation : int
        Current generation number.
    live_cells : int
        Number of live cells in current generation.
    is_running : bool
        Whether the simulation is currently running.
    selected_pattern : str
        Name of the currently selected pattern.
    """

    grid: np.ndarray
    generation: int
    live_cells: int
    is_running: bool
    selected_pattern: str


class SimulationController:
    """Controller for managing Game of Life simulation state."""

    def __init__(self, grid_size: tuple[int, int] = (50, 50)):
        """Initialize the simulation controller.

        Parameters
        ----------
        grid_size : tuple[int, int]
            Size of the grid (rows, cols).
        """
        self.grid_size = grid_size
        self.pattern_library = PatternLibrary()
        self.engine = GameOfLifeEngine()

        self._current_grid: Optional[np.ndarray] = None
        self._initial_grid: Optional[np.ndarray] = None
        self._generation: int = 0
        self._is_running: bool = False
        self._selected_pattern: str = "glider"

    def initialize(self, pattern_name: str) -> None:
        """Initialize the simulation with a pattern.

        Parameters
        ----------        pattern_name : str
            Name of the pattern to initialize with.
        """
        self._selected_pattern = pattern_name
        self._current_grid = self.engine.initialize_grid(pattern_name, self.grid_size, self.pattern_library)
        self._initial_grid = self._current_grid.copy()
        self._generation = 0
        self._is_running = False

    def step_forward(self) -> None:
        """Execute one simulation step (compute next generation)."""
        if self._current_grid is None:
            raise RuntimeError("Simulation not initialized. Call initialize() first.")

        self._current_grid = self.engine.compute_next_generation(self._current_grid)
        self._generation += 1

    def start_simulation(self) -> None:
        """Start the simulation (mark as running)."""
        if self._current_grid is None:
            raise RuntimeError("Simulation not initialized. Call initialize() first.")
        self._is_running = True

    def pause_simulation(self) -> None:
        """Pause the simulation."""
        self._is_running = False

    def reset_simulation(self) -> None:
        """Reset the simulation to initial state."""
        if self._initial_grid is None:
            raise RuntimeError("Simulation not initialized. Call initialize() first.")

        self._current_grid = self._initial_grid.copy()
        self._generation = 0
        self._is_running = False

    def get_current_state(self) -> SimulationState:
        """Get the current simulation state.

        Returns
        -------
        SimulationState
            Current state of the simulation.
        """
        if self._current_grid is None:
            # Return empty state if not initialized
            return SimulationState(
                grid=np.zeros(self.grid_size, dtype=np.int8),
                generation=0,
                live_cells=0,
                is_running=False,
                selected_pattern=self._selected_pattern,
            )

        live_cells = int(np.sum(self._current_grid))

        return SimulationState(
            grid=self._current_grid.copy(),
            generation=self._generation,
            live_cells=live_cells,
            is_running=self._is_running,
            selected_pattern=self._selected_pattern,
        )

    def get_pattern_list(self) -> list[str]:
        """Get list of available patterns.

        Returns
        -------
        list[str]
            List of pattern names, including 'random'.
        """
        patterns = self.pattern_library.get_pattern_list()
        patterns.append("random")
        return sorted(patterns)

    @property
    def generation(self) -> int:
        """Get current generation number."""
        return self._generation

    @property
    def is_running(self) -> bool:
        """Check if simulation is running."""
        return self._is_running

    @property
    def grid(self) -> Optional[np.ndarray]:
        """Get current grid state."""
        return self._current_grid.copy() if self._current_grid is not None else None
