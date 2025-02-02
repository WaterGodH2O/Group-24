from typing import List
from Lane import Lane

class Arm:
    """
    This class defines the behaviour of each entrance in the junction
    """
    def __init__(self, length: int, width: int, vehicles_per_hour: List[int]):
        # the length of the junction and numbner of lanes in the junction
        self._length: int = length
        self._width: int = width

        # !! should i use north, south, east west instead?
        # the number of vehicles expected per hour. Index 0 = going left, 1 = forward, 2 = right
        self._vehicles_per_hour: List[int] = vehicles_per_hour

        # initalise a list of all the lanes coming from a certain direction in the junction
        # TODO assign lanes
        self._lanes: List[Lane] = []

        # represents the most cars in the arm at any given point in the simulation
        self._max_queue_length: int = 0

    @property
    def length(self) -> int:
        """ Returns the length of the arm """
        return self._length
    
    @property
    def width(self) -> int:
        """ Returns the width of the arm """
        return self._width
    
    @property
    def max_queue_length(self) -> int:
        """ Returns the longest queue seen at any given point """
        return self._max_queue_length
    
    def move_all_vehicles(self) -> None:
        """
        Method to update all the vehicles in each lane of the junction +
        allocate new vehicles to lanes
        """
        # TODO implement this method
        pass
