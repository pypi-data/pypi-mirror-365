"""Class representing a Hex grid. Particular map implementations should subclass this."""
import queue
from abc import abstractmethod, ABC
from typing import Dict, Tuple, List
from dataclasses import dataclass, field
from .hex import Hex


@dataclass(order=True)
class PrioritizedHex:
    """
    Placeholder class for Hexes in a priority Queue.

    Attributes
    ----------
    priority : int
        the priority of the item in the queue

    item : Hex
        the Hex associated with priority `priority`
    """
    priority: int
    item: Hex = field(compare=False)


class HexGrid(ABC):
    """
    Class representing the Hex grid used by the map.

    Attributes
    ----------
    layout : Layout
        the layout of the grid

    grid : List[List[Hex]]
        2D array holding Hexes

    flat_grid : List[Hex]
        flattened array of Hexes, exists for convenience

    graph : Dict[Hex, List[Hex]]
        Graph representing the grid, associates every Hex to its neighbours on the grid

    Methods
    -------
    dijkstra_search(start: Hex, target: Hex)
        pathfinding algorithm between `start` and `target` on the grid

    movement_cost(h: Hex)
        return movement cost of a Hex on the grid

    compute_pathfinding(start: Hex, target: Hex)
        wrapper function around pathfinding operations. Returns a (path, cost) tuple.
    """
    def __init__(self, dimensions: Tuple[int, int]):
        self.grid = [[Hex(q, s) for q in range(dimensions[0])] for s in range(dimensions[1])]
        self.flat_grid = [h for _ in self.grid for h in _]
        # filter is a generator : once pathfinding is done ONCE it is empty
        self.graph = {h: list(filter(lambda x: x in self.flat_grid, h.neighbours())) for h in self.flat_grid}

    def dijkstra_search(self, start: Hex, target: Hex) -> Tuple[Dict[Hex, Hex], Dict[Hex, int]]:
        """
        Simple pathfinding using the dijkstra's search algorithm.

        Parameters
        ----------
        start : Hex
            The Hex from which to search.
        target : Hex
            The Hex to path to.

        Returns
        -------
        Tuple[Dict[Hex, Hex], Dict[Hex, int]]
            A tuple containing a dict of visited Hexes and a dict of {Hex: movement_cost} pairs.
        """
        frontier = queue.PriorityQueue()
        frontier.put(PrioritizedHex(0, start), block=False)
        came_from = {}
        cost_so_far: Dict[Hex, int] = {start: 0}
        while not frontier.empty():
            current = frontier.get().item
            if current == target:
                return came_from, cost_so_far
            for next_node in self.graph[current]:
                new_cost = cost_so_far[current] + self.movement_cost(next_node)
                if new_cost < cost_so_far.get(next_node, 100):
                    cost_so_far[next_node] = new_cost
                    frontier.put(PrioritizedHex(new_cost, next_node))
                    came_from[next_node] = current
        return came_from, cost_so_far

    @abstractmethod
    def movement_cost(self, h: Hex) -> int:
        """
        Return the movement cost of the passed Hex.

        Parameters
        ----------
        h:
            The Hex whose movement cost to get.

        Returns
        -------
        Must be implemented by the subclass.
        """
        raise NotImplementedError

    @staticmethod
    def reconstruct_path(came_from: Dict[Hex, Hex], start: Hex, target: Hex) -> List[Hex]:
        """
        Return the shortest path from 'start' to 'target'.

        Parameters
        ----------
        came_from : Dict[Hex, Hex]
            the nested graph computed by dijkstra_search
        start : Hex
            the Hex from which to start
        target : Hex
            the Hex to reach

        Returns
        -------
        List[Hex]
            A list of Hexes in order of visit.
        """
        current = target
        path = []
        if target not in came_from:
            return []
        while current != start:
            path.append(current)
            current = came_from[current]
        path.append(start)
        path.reverse()
        return path

    def compute_pathfinding(self, start: Hex, target: Hex) -> Tuple[List[Hex], Dict[Hex, int]]:
        """
        Helper function wrapping pathfinding operations.

        Return a tuple containing the shortest path to 'target' from 'start' and a dict of costs.

        Parameters
        ----------
        start : Hex
            the starting Hex
        target : Hex
            the target Hex

        Returns
        -------
        Tuple[List[Hex], Dict[Hex, int]]
            A tuple containing the shortest path as a list of Hexes and the dict of costs, in that order.
        """
        came_from, cost_so_far = self.dijkstra_search(start, target)
        path = HexGrid.reconstruct_path(came_from, start, target)
        return path, cost_so_far
