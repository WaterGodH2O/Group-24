from typing import List
from Lane import CarLane, Lane
from time import time
from math import ceil

class Arm:
    """
    This class defines the behaviour of each entrance in the junction
    """
    def __init__(self, width: int, length: int, vehicles_per_hour: List[int], num_lanes: int):
        # the length and width of the arm in metres
        self._length: int = length
        self._width: int = width

        # the number of seconds until a vehicle is expected Index 0 = north, 1 = east, 2 = south, 3 = west
        self._seconds_per_vehicle: List[int] = list(map(lambda vph : ceil(3600 / vph), vehicles_per_hour))

        # initalise a list of all the lanes coming from a certain direction in the junction
        # TODO assign lanes
        self._lanes: List[Lane] = []
        for i in range(num_lanes):
            self._lanes.append(CarLane([0, 1, 2, 3], width / num_lanes, length))

        # represents the most cars in the arm at any given point in the simulation
        self._max_queue_length: int = 0

        # how long each car has been in the arm
        self._total_wait_times: float = 0
        
        # the total number of vehicles that have left the junction
        self._total_car_count: int = 0

        # the longest any given vehicle has been waiting in the arm
        self._max_wait_time: float = 0

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
    
    def move_all_vehicles(self, isLightGreen: bool) -> None:
        """
        Method to update all the vehicles in each lane of the junction + allocate new vehicles to lanes
        """
        
        # move each vehicle currently in the lane
        for lane in self._lanes:
            # update the position of each vehicle in the arm
            vehicle_leaving = lane.move_all_vehicles(isLightGreen)

            # remove the vehicles from the lane if necessary
            if vehicle_leaving:
                lane.remove_vehicle(vehicle_leaving)

                # update kpi
                self._total_wait_times += time() -  vehicle_leaving.arrival_time
                self._total_car_count += 1
            
            # update the max wait time
            self._max_wait_time = max(self._max_wait_time, lane.get_longest_wait_time())
            
        #TODO: lane change

        #TODO: assign new vehicles to lanes


    
    def get_kpi(self) -> List[float]:
        # calculate the efficiency
        average_wait_time = self._total_wait_times / self._total_car_count if self._total_car_count != 0 else 0
        kpi_efficiency = average_wait_time + self._max_wait_time + self._max_queue_length # TODO placeholder until we get proper formula
        
        # return the key kpi stats
        return [kpi_efficiency, average_wait_time, self._max_wait_time, self._max_queue_length]
        
    def no_vehicles_within(self, distance: int) -> bool:
        """ 
        Check if any vehicles are within a given distance from the junction 
        
        :param distance: The distance from the junction to check
        :return: False if no vehicles are close enough, true otherwise.
        """
        for lane in self._lanes:
            if lane.get_first_vehicle() and lane.get_first_vehicle().distance < distance:
                return False
        return True
    
    def create_vehicle(self, speed: int, source: int, destination: int, type: str, lane: int = 0):
        """ Create a new vehicle in a given lane """
        self.get_lane(lane).create_vehicle(speed, source, destination, type)