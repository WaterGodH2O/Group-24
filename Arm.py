from typing import List
from Lane import Lane, CarLane, BusLane, LeftTurnLane
from exceptions import TooManyVehiclesException, NotEnoughLanesException
from Box import Box
from bisect import bisect_right

class Arm:
    """
    This class defines the behaviour of each entrance in the junction
    """
    def __init__(self, 
                 width: int, 
                 length: int, 
                 vehicles_per_hour: List[int], 
                 num_lanes: int, 
                 num_arms: int, 
                 bus_lane: bool, 
                 left_turn_lane: bool):
        # the length and width of the arm in metres
        self._length: int = length
        self._width: int = width

        # the number of vehicles expected per hour. Index 0 = north, 1 = east, 2 = south, 3 = west
        self._vehicles_per_hour: List[int] = vehicles_per_hour

        # initalise a list of all the lanes coming from a certain direction in the junction
        self._lanes: List[Lane] = []
        if(bus_lane):
            self._lanes.append(BusLane(width / num_lanes, length, num_arms))
            num_lanes -= 1
        if(left_turn_lane):
            try:
                self._lanes.append(LeftTurnLane(width / num_lanes, length, num_arms))
                num_lanes -= 1
            except ZeroDivisionError:
                #If num lanes is zero, then ignore the error as a notenoughlanes error will be thrown immediately afterwards
                pass

        if num_lanes < 1:
            raise NotEnoughLanesException()
        
        for i in range(num_lanes):
            self._lanes.append(CarLane(width / num_lanes, length, num_arms))

        # represents the most cars in the arm at any given point in the simulation
        self._max_queue_length: int = 0

        # how long each car has been in the arm in seconds
        self._total_wait_times: float = 0
        
        # the total number of vehicles that have left the junction
        self._total_car_count: int = 0

        # the longest any given vehicle has been waiting in the arm in seconds
        self._max_wait_time: float = 0

        # the number of people that have left the junction
        self._total_person_count: int = 0

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
    
    def move_all_vehicles(self, current_time_ms: int, traffic_light_dir: int, junction_box: Box, update_length_ms: int, num_arms: int, arm_id: int) -> None:
        """
        Method to update all the vehicles in each lane of the junction + allocate new vehicles to lanes
        Moves all the vehicles for a particular arm in the junction. For each vehicle that exits the lane,
        it updates the KPI attributes

        :param current_time_ms: How long the simulation has been running for in milliseconds
        :param is_light_green: Whether the traffic light for this lane is green or not
        """
        
        for i, lane in enumerate(self._lanes):
            # update the position of each vehicle in the arm, getting the vehicle leaving the lane
            vehicles_leaving = lane.move_all_vehicles(traffic_light_dir, update_length_ms, junction_box, arm_id, i, num_arms)

            # remove the vehicles from the lane if necessary
            for vehicle_leaving in vehicles_leaving:
                lane.remove_vehicle(vehicle_leaving)
                junction_box.add_vehicle(vehicle_leaving)
                # update kpi
                vehicle_wait_time = vehicle_leaving.wait_time / 1000 # in seconds
                #print(f"{vehicle_leaving.vehicle_type} entered box from arm {vehicle_leaving.source}, lane {vehicle_leaving.source_lane}, turning {vehicle_leaving.get_relative_direction(num_arms)}")
                self._max_wait_time = max(self._max_wait_time, vehicle_wait_time)
                self._total_wait_times += vehicle_wait_time
                self._total_car_count += 1

            
            # update the max queue length
            self._max_queue_length = max(self._max_queue_length, lane.queue_length)  
            
        # change lanes
        self.handle_lane_switching(num_arms)

    def handle_lane_switching(self, num_arms):
        """ Attempts lane switching for all vehicles in the arm of a junction, prioritising shortest lane """

        previous_lane = None
        vehicles_to_remove = [] # list of vehicles and what lane we want to remove them from

        for i, current_lane in enumerate(self._lanes):
            
            # get adjacent lanes
            adjacent_lanes: list[Lane] = []
            if previous_lane:
                adjacent_lanes.append(previous_lane)
            if i < len(self._lanes) - 1:
                adjacent_lanes.append(self._lanes[i + 1])

            
            for vehicle in current_lane.vehicles:
                # sort the adjacent lanes by min queue_length to prioritise shorter lanes
                adjacent_lanes.sort(key=lambda lane: lane.queue_length)

                for new_lane in adjacent_lanes:
                    # check if the vehicle can merge into a new lane if the current lane is shorter
                    # and goes where the vehicle wants to go
                    if self.is_new_lane_shorter(current_lane, new_lane) and new_lane.can_enter_lane(vehicle, num_arms):
                        
                        # stop looping if the vehicle has successfully merged into the new lane
                        if self.move_vehicle_to_lane(vehicle, current_lane, new_lane):
                            vehicles_to_remove.append((current_lane, vehicle))
                            break

            # update the previous lane
            previous_lane = current_lane
        
        # remove all vehicles from the lanes they have switched to
        for lane, vehicle in vehicles_to_remove:
            lane.remove_vehicle(vehicle)

    def move_vehicle_to_lane(self, vehicle, current_lane, target_lane):
        """
        Moves a given vehicle into a new lane at a specified position

        :param vehicle: the vehicle we want to move
        :param current_lane: the lane the vehicle is currently in
        :param target_lane: the lane we want to move the vehicle to
        """

        # the index the vehicle will be added to in teh target lane
        new_lane_index = self.enough_space_to_merge(vehicle, target_lane)
        if new_lane_index != -1:

            # add vehicle to new lane at specified index
            target_lane.add_vehicle_to_index(vehicle, new_lane_index)

            # update current lane count (as if the vehicle has been removed) to ensure proper sorting
            current_lane._queue_length -= 1

            # return true, indicating vehicle has merged successfully
            return True

        # return false as no merge was possible
        return False

    
    def enough_space_to_merge(self, vehicle, lane):
        """ 
        Checks if there is enough space for a given vehicle to fit in a new lane
        
        :param vehicle: the vehicle we want to add to the new lane
        :param lane: the lane we want to add the vehicle to
        :return: the index the new vehicle can merge into, -1 otherwise
        """
        # check if there is enough space for a vehicle in a new lane
        
        # perform a binary search to find the index where the new vehicle would be inserted
        vehicle_positions_arr = [v.distance for v in lane.vehicles]
        new_vehicle_index = bisect_right(vehicle_positions_arr, vehicle.distance)

        # find the vehicle ahead and behind of where the vehicle would be
        vehicle_ahead = lane.vehicles[new_vehicle_index - 1] if new_vehicle_index > 0 else None
        vehicle_behind = lane.vehicles[new_vehicle_index] if new_vehicle_index < len(lane.vehicles) else None

        # check the space between the vehicle ahead and behind to ensure adequate space
        if vehicle_ahead and vehicle.distance - vehicle_ahead.distance <= vehicle._stopping_distance:
            # return -1 to indicate we can't move into this lane
            return -1
        
        # check if there is enough space for the vehicle behind to adequately stop
        if vehicle_behind and vehicle_behind.distance - vehicle.distance <= vehicle_behind._stopping_distance:
            return -1

        # return the index the vehicle should be isnerted
        return new_vehicle_index

    def is_new_lane_shorter(self, current_lane, new_lane):
        """ Checks if there is at least two cars difference between two adjacent lanes """
        return current_lane.queue_length - new_lane.queue_length > 1

    
    def get_kpi(self) -> List[float]:
        """ Returns the key performance indicators for this arm of the junction """
        # calculate the efficiency
        total_wait_time = self._total_wait_times
        max_wait_time = self._max_wait_time

        # include all current vehicles in wait time calculations
        for lane in self._lanes:
            for vehicle in lane.vehicles:
                vehicle_wait_time = vehicle.wait_time / 1000
                total_wait_time += vehicle_wait_time
                
                # update max wait time if necessary
                if vehicle_wait_time > max_wait_time:
                    max_wait_time = vehicle_wait_time

        
        total_vehicles = self._total_car_count + sum(len(lane.vehicles) for lane in self._lanes)
        average_wait_time = total_wait_time / total_vehicles if total_vehicles != 0 else 0
        
        # return the key kpi stats
        return [round(average_wait_time, 1), round(max_wait_time, 1), self._max_queue_length]

    def get_total_car_count(self) -> int:
        """Returns total car count for this arm of the junction"""
        return self._total_car_count
    
    def get_current_queue_length(self) -> int:
        """ Returns the length of the largest queue of vehicles currently in this arm of the junction to be used for graphing"""
        return max([lane.queue_length for lane in self._lanes])
    
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
    

    def create_vehicle(self, speed: int, source: int, destination: int, type: str, num_arms:int) -> None:
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
        
        for i in range(0, len(self._lanes)):
            v = self._lanes[i].create_vehicle(speed, source, destination, type, start_position, num_arms)
            if v:
                #print(f"{v._vehicle_type} created in arm {source} lane {i}, turning {v.get_relative_direction(num_arms)}")
                break
                
