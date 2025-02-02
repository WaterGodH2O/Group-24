from typing import List
from abc import ABC, abstractmethod
from Vehicle import Vehicle


class Lane(ABC):
    """
    The abstract class Lane, which defines the basic interface for all lanes.
    """
    def __init__(self, allowed_directions: List[int], width: int, length: int):
        # the list of all vehicles currently in this lane
        self._vehicles: List[Vehicle] = []

        # the directions vehicles in this lane can go
        self._allowed_directions: List[int] = allowed_directions

        # the width of the lane
        self._width: int = width
        self._length: int = length

    @property
    def allowed_directions(self) -> List[int]:
        """ Returns the directions cars in this lane are allowed to travel """
        return self._allowed_directions
    @property
    def width(self) -> int:
        return self._width
    @property
    def length(self) -> int:
        return self._length

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
        """
        # TODO might need to be changed
        # add the given vehicle to the end of the lane
        self._vehicles.append(vehicle)

    def remove_vehicle(self, vehicle: Vehicle) -> None:
        """
        Removes a given vehicle from the current lane should they enter the box / switch lanes
        """
        # TODO might need to be changed
        # remove a specific vehicle from the list
        self._vehicles.remove(vehicle)
    
    @abstractmethod
    def move_all_vehicles(self) -> None:
        """
        Abstract method to update the positions of all vehicles in the lane, including lane arrivals and departures
        """
        pass

    @property
    @abstractmethod
    def can_enter_junction(self) -> bool:
        """
        Indicate whether the vehicle in this lane are allowed to enter junction
        i.e. whether cooresponding traffic light is green.
        """
        pass


class CarLane(Lane):
    def __init__(self, allowed_directions: List[int], width: int, length: int):
        super().__init__(allowed_directions, width, length)

    def move_all_vehicles(self) -> None:
        # TODO implement this method
        pass

    def can_enter_junction(self) -> bool:
        # TODO implement this method
        return False


# !! not a must have requirement
class BusLane(Lane):

    def __init__(self, allowed_directions: List[int], width: int, length: int):
        super().__init__(allowed_directions, width, length)

    def move_all_vehicles(self) -> None:
        # TODO implement this method
        pass

    def can_enter_junction(self) -> bool:
        # TODO implement this method
        return False