from typing import List
from Lane import CarLane, Lane
from exceptions import TooManyVehiclesException
from Box import Box

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
        return self._lanes[lane_num] if lane_num < len(self._lanes) else None
    
    def move_all_vehicles(self, current_time_ms: int, is_light_green: bool, junction_box: Box, update_length_ms: int, num_arms: int) -> None:
        """
        Method to update all the vehicles in each lane of the junction + allocate new vehicles to lanes
        Moves all the vehicles for a particular arm in the junction. For each vehicle that exits the lane,
        it updates the KPI attributes

        :param current_time_ms: How long the simulation has been running for in milliseconds
        :param is_light_green: Whether the traffic light for this lane is green or not
        """
        
        for i, lane in enumerate(self._lanes):
            # update the position of each vehicle in the arm, getting the vehicle leaving the lane
            vehicle_leaving = lane.move_all_vehicles(is_light_green, update_length_ms, junction_box, i, num_arms)

            # remove the vehicles from the lane if necessary
            if vehicle_leaving:
                lane.remove_vehicle(vehicle_leaving)
                print(f"Vehicle moved to box")
                junction_box.add_vehicle(vehicle_leaving)
                # update kpi
                vehicle_wait_time = (current_time_ms - vehicle_leaving.arrival_time) / 1000

                self._max_wait_time = max(self._max_wait_time, vehicle_wait_time)
                self._total_wait_times += vehicle_wait_time
                self._total_car_count += 1
            
            # update the max queue length
            self._max_queue_length = max(self._max_queue_length, lane.length)
            
            
        #TODO: lane change

        #TODO: assign new vehicles to lanes
        #! might already be done in Junction.py so not necessary here


    
    def get_kpi(self) -> List[float]:
        """ Returns the key performance indicators for this arm of the junction """
        # calculate the efficiency
        average_wait_time = self._total_wait_times / self._total_car_count if self._total_car_count != 0 else 0
        
        # return the key kpi stats
        return [average_wait_time, self._max_wait_time, self._max_queue_length]
        
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
    

    def create_vehicle(self, speed: int, source: int, destination: int, type: str) -> None:
        """ Create a new vehicle in a random lane """
        furthest_car_distance = 0
        for lane in self._lanes:
            vehicle = lane.get_last_vehicle()
            if vehicle == None:
                dist = 0
            else:
                dist = vehicle.distance
            furthest_car_distance = max(furthest_car_distance, dist)
        start_position = furthest_car_distance + 20
        if start_position > self._length:
            raise TooManyVehiclesException
        self._lanes[0].create_vehicle(speed, source, destination, type, start_position)