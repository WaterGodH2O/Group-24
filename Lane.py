from typing import List, Set
from abc import ABC, abstractmethod
from Vehicle import Vehicle, Car, Bus
from Box import Box

class Lane(ABC):
    """
    The abstract class Lane, which defines the basic interface for all lanes.
    """
    def __init__(self, allowed_directions: List[int], width: int, length: int):
        # the list of all vehicles currently in this lane
        self._vehicles: List[Vehicle] = []

        # the directions vehicles in this lane can go
        self._allowed_directions: Set[int] = set(allowed_directions)

        # the width of the lane
        self._width: int = width
        self._length: int = length

        # the number of vehicles currently in the lane
        self._queue_length: int = 0

    @property
    def allowed_directions(self) -> Set[int]:
        """ Returns the directions cars in this lane are allowed to travel """
        return self._allowed_directions
    @property
    def vehicles(self) -> List[Vehicle]:
        return self._vehicles
    @property
    def width(self) -> int:
        return self._width
    @property
    def length(self) -> int:
        return self._length
    @property
    def queue_length(self) -> int:
        return self._queue_length

    def get_first_vehicle(self) -> Vehicle:
        """
        Method to get the first vehicle currently in this lane

        :return: The first vehicle in the lane or None if the list is empty
        """
        
        # return the first index of the list or none if empty
        return self._vehicles[0] if self._vehicles else None
    
    def get_last_vehicle(self) -> Vehicle:
        """
        Method to get the last vehicle currently in this lane

        :return: The last vehicle in the lane or None if the list is empty
        """
        
        # return the last index of the list or none if empty
        return self._vehicles[-1] if self._vehicles else None
    
    def get_vehicle_ahead(self, current_vehicle: Vehicle) -> Vehicle:
        """
        Method to get the vehicle in front of a given vehicle

        :param current_vehicle: The vehicle which we want to find the next vehicle from
        :return: The next vehicle in the lane or None if the list is empty
        """
        try:
            # try to find the index of the vehicle in front of the current vehicle
            vehicle_ahead_index = self._vehicles.index(current_vehicle) - 1
            
            # return None if there aren't any vehicles in front of the current vehicle
            if vehicle_ahead_index < 0:
                return None
            
            # return the vehicle in front of the current vehicle
            return self._vehicles[vehicle_ahead_index]
            
        # return None if we can't find the position of the current vehicle
        except ValueError:
            return None
    
    def add_vehicle(self, vehicle: Vehicle) -> None:
        """
        Method to add a vehicle to the end of the current lane

        :param vehicle: The vehicle we want to add
        """
        # add the given vehicle to the end of the lane
        self._vehicles.append(vehicle)
        self._queue_length += 1

    def add_vehicle_to_index(self, vehicle: Vehicle, index: int) -> None:
        """ Method do add a vehicle to a specified index """
        self._vehicles.insert(index, vehicle)
        self._queue_length += 1


    def remove_vehicle(self, vehicle: Vehicle) -> Vehicle:
        """
        Removes a given vehicle from the current lane should they enter the box / switch lanes

        :param vehicle: The vehicle we want to remove
        :return: The vehicle removed or None if not found
        """
        # remove a specific vehicle from the list if found
        if vehicle in self._vehicles:
            self._vehicles.remove(vehicle)
            self._queue_length = len(self._vehicles)
            return vehicle
        return None
    
    
    def move_all_vehicles(self, is_light_green: bool, update_length_ms: int, box: Box, lane_id: int, num_arms: int) -> Vehicle:
        """
        Moves all vehicles in the lane based on speed. Cars can move if there is sufficient space
        ahead of them, or if they're at the start of the junction and the light is green

        :param is_light_green: Whether the traffic light for this lane is green or not
        :return: the vehicles currently leaving the junction
        """
        leaving_vehicle = None
        vehicle_ahead = None

        for i, vehicle in enumerate(self._vehicles):
            # enter the box if at a junction
            if i == 0 and vehicle._distance <= 0:
                if self.can_enter_box(vehicle, box, lane_id, is_light_green, num_arms):
                    # this vehicle will leave the junction
                    vehicle.set_source_lane(lane_id)
                    leaving_vehicle = vehicle
                else:
                    # update the wait time if they can't enter the junction
                    vehicle.update_wait_time(update_length_ms)

            # if the vehicle is at the front of the queue and not at the junction (no need to check vehicle ahead)
            elif i == 0 or vehicle_ahead == leaving_vehicle:
                vehicle.set_position(vehicle.get_next_position(update_length_ms))

            # update vehicle distance if there is enough space to move forward
            elif self.has_space_to_move(vehicle, vehicle_ahead):
                # new position is the furthest the vehicle can travel in the time step ensuring it doesn't get too
                # close to the vehicle ahead
                new_vehicle_distance = max(vehicle.get_next_position(update_length_ms),
                                           vehicle_ahead.distance + vehicle._stopping_distance)
                
                vehicle.set_position(new_vehicle_distance)

            # update the wait time if the vehicle doesn't have space to move
            else:
                vehicle.update_wait_time(update_length_ms)

            # update the vehicle ahead for the next iteration
            vehicle_ahead = vehicle

        return leaving_vehicle
        
    def has_space_to_move(self, vehicle, vehicle_ahead):
        """ checks if there is any space between a vehicle and the car ahead """
        if vehicle_ahead is None:
            return True
        return vehicle.distance > vehicle_ahead.distance + vehicle._stopping_distance
        

    
    def get_earliest_wait_time(self) -> float:
        """
        Method to return the longest wait time currently in the queue. Intuition is the first vehicle will
        always have been waiting for longer than the vehicles behind it as it entered first

        :return: longest wait time present in the lane
        """
        return self._vehicles[0].wait_time if self._vehicles else 0

    def can_enter_box(self, vehicle: Vehicle, box: Box, lane_id: int, is_light_green: bool, num_arms: int) -> bool:
        """
        Indicate whether the vehicle in this lane are allowed to enter junction
        i.e. whether cooresponding traffic light is green.
        """
        #If the light is red, do not enter.
        if (not is_light_green):
            return False
        
        #Vehicle's relative direction. 1 = right, 2 = forward, 3 = left
        #For more/less arms, represents the number of arms anticlockwise
        vehicle_relative_dir = (vehicle.source - vehicle.destination) % num_arms

        for box_vehicle in box.get_vehicles():
            box_v_r_d = (box_vehicle.source - box_vehicle.destination) % num_arms
            #If a vehicle came from a lane to the left
            if box_vehicle.source_lane < lane_id:
                #If the box vehicle is moving somewhere right of the vehicles target, it blocks.
                #Eg: if the box vehicle is moving forwards (2), it blocks left (3) turns.
                if box_v_r_d < vehicle_relative_dir:
                    return False

            #If a vehicle came from the right
            elif box_vehicle.source_lane > lane_id:
                #If the box vehicle is moving somewhere right of the vehicles target, it blocks.
                if box_v_r_d > vehicle_relative_dir:
                    return False
        #If the light is green and no vehicle in the box blocks it, enter the box
        return True

    @abstractmethod
    def create_vehicle(self, speed: int, source: int, destination: int, type: str) -> bool:
        """
        Create a new vehicle, unless forbidden by lane type
        :return: True if created successfully, false otherwise.
        """


class CarLane(Lane):
    def __init__(self, allowed_directions: List[int], width: int, length: int):
        super().__init__(allowed_directions, width, length)
    
    def create_vehicle(self, speed: int, source: int, destination: int, type: str, start_position: int) -> bool:
        """
        Create a new vehicle with the given information.
        """
        if type == "Car":
            self.add_vehicle(Car(speed, source, destination, start_position))
            return True
        if type == "Bus":
            self.add_vehicle(Bus(speed, source, destination, start_position))
            return True
        return False


# !! not a must have requirement
class BusLane(Lane):

    def __init__(self, allowed_directions: List[int], width: int, length: int):
        super().__init__(allowed_directions, width, length)
    
    def create_vehicle(self, speed: int, source: int, destination: int, type: str) -> bool:
        if type == "Bus":
            self.add_vehicle(Bus(speed, source, destination, 150))
            return True
        return False

