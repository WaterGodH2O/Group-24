from typing import List
from abc import ABC, abstractmethod
from Vehicle import Vehicle, Car, Bus


class Lane(ABC):
    """
    The abstract class Lane, which defines the basic interface for all lanes.
    """
    def __init__(self, allowed_directions: List[int], width: int, length: int):
        # the list of all vehicles currently in this lane
        self._vehicles: List[Vehicle] = []

        # the directions vehicles in this lane can go
        self._allowed_directions: set[int] = set(allowed_directions)

        # the width of the lane
        self._width: int = width
        self._length: int = length

    @property
    def allowed_directions(self) -> set[int]:
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

    def remove_vehicle(self, vehicle: Vehicle) -> Vehicle:
        """
        Removes a given vehicle from the current lane should they enter the box / switch lanes

        :param vehicle: The vehicle we want to remove
        :return: The vehicle removed or None if not found
        """
        # remove a specific vehicle from the list if found
        if vehicle in self._vehicles:
            self._vehicles.remove(vehicle)
            return vehicle
        return None
    
    def move_all_vehicles(self, is_light_green: bool, update_length_ms: int) -> Vehicle:
        """
        Moves all vehicles in the lane based on speed. Cars can move if there is sufficient space
        ahead of them, or if they're at the start of the junction and the light is green

        :param is_light_green: Whether the traffic light for this lane is green or not
        :return: the vehicles currently leaving the junction
        """
        leaving_vehicle = None

        for i, vehicle in enumerate(self._vehicles):
            # enter the box if at a junction
            if i == 0 and vehicle._distance <= 0:
                if is_light_green:
                    # this vehicle will leave the junction
                    leaving_vehicle = vehicle

            # update vehicle distance if there is enough space to move forward
            elif i == 0 or vehicle._distance - vehicle._stopping_distance > self._vehicles[i - 1]._distance or self._vehicles[i - 1] == leaving_vehicle:
                vehicle._distance -= vehicle._speed * update_length_ms / 1000

        return leaving_vehicle
        
    def get_earliest_arrival_time(self) -> float:
        """
        Method to return the longest wait time currently in the queue. Intuition is the first vehicle will
        always have been waiting for longer than the vehicles behind it as it entered first

        :return: longest wait time present in the lane
        """
        return self._vehicles[0].arrival_time if self._vehicles else 0


    @property
    @abstractmethod
    def can_enter_junction(self) -> bool:
        """
        Indicate whether the vehicle in this lane are allowed to enter junction
        i.e. whether cooresponding traffic light is green.
        """
        pass

    @abstractmethod
    def create_vehicle(self, speed: int, source: int, destination: int, type: str) -> bool:
        """
        Create a new vehicle, unless forbidden by lane type
        :return: True if created successfully, false otherwise.
        """


class CarLane(Lane):
    def __init__(self, allowed_directions: List[int], width: int, length: int):
        super().__init__(allowed_directions, width, length)

    def can_enter_junction(self) -> bool:
        # TODO implement this method
        return False
    
    def create_vehicle(self, speed: int, source: int, destination: int, type: str, arrival_time) -> bool:
        # TODO replace 150 with max(80% of lane length, last_vehicle.position) 
        if type == "Car":
            self.add_vehicle(Car(speed, source, destination, 150, arrival_time))
            return True
        if type == "Bus":
            self.add_vehicle(Bus(speed, source, destination, 150, arrival_time))
            return True
        return False


# !! not a must have requirement
class BusLane(Lane):

    def __init__(self, allowed_directions: List[int], width: int, length: int):
        super().__init__(allowed_directions, width, length)

    def can_enter_junction(self) -> bool:
        # TODO implement this method
        return False
    
    def create_vehicle(self, speed: int, source: int, destination: int, type: str) -> bool:
        if type == "Bus":
            self.add_vehicle(Bus(speed, source, destination, 150))
            return True
        return False
