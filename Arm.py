from typing import List
from Lane import CarLane, Lane

class Arm:
    """
    This class defines the behaviour of each entrance in the junction
    """
    def __init__(self, width: int, length: int, vehicles_per_hour: List[int], num_lanes: int):
        # the length and width of the arm in metres
        self._length: int = length
        self._width: int = width

        # the number of vehicles expected per hour. Index 0 = north, 1 = east, 2 = south, 3 = west
        self._vehicles_per_hour: List[int] = vehicles_per_hour

        # initalise a list of all the lanes coming from a certain direction in the junction
        # TODO assign lanes
        self._lanes: List[Lane] = [None] * num_lanes
        for i in range(len(self._lanes)):
            self._lanes[i] = CarLane([0, 1, 2, 3], width / num_lanes, length)

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
    
    def get_lane(self, lane_num: int) -> Lane:
        return self._lanes[lane_num]
    
    def move_all_vehicles(self) -> None:
        """
        Method to update all the vehicles in each lane of the junction +
        allocate new vehicles to lanes
        """
        #TODO: lane changes

        #TODO: handle functionality if lights are green

        #TODO: assign new vehicles to lanes

        pass
