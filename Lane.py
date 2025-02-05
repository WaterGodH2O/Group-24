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
    def vehicles(self) -> List[Vehicle]:
        return self._vehicles
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
    
    def move_all_vehicles(self) -> List[Vehicle]:
        """
        Method to update the distance of all vehicles in the lane

        :param elapsed_time: How long the vehicle has been in the queue for
        :return: the vehicles currently leaving the junction
        """
        leaving_vehicles = []

        for i, car in enumerate(self._vehicles):
            # enter the box if at a junction
            if i == 0 and car._distance == 0:
                # TODO enter box junction, leave current queue
                if self.can_enter_junction():
                    # add the vehicles exiting the junction to a queue
                    leaving_vehicles.append(car)
                    pass

            # if there is enough space to move forward
            elif i == 0 or car._distance - car._stopping_distance > self._vehicles[i - 1]._distance:
                # TODO add an elapsed_time to Vehicle.py to update the distance of the car
                # car._distance -= car._speed * car.elapsed_time
                pass

        return leaving_vehicles
        
    def get_longest_wait_time(self) -> float:
        """
        Method to return the longest wait time currently in the queue. Intuition is the first vehicle will
        always have been waiting for longer than the vehicles behind it as it entered first

        :return: longest wait time present in the lane
        """
        return self._vehicles[0].waiting_time if self._vehicles else 0


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

    def can_enter_junction(self) -> bool:
        # TODO implement this method
        return False


# !! not a must have requirement
class BusLane(Lane):

    def __init__(self, allowed_directions: List[int], width: int, length: int):
        super().__init__(allowed_directions, width, length)

    def can_enter_junction(self) -> bool:
        # TODO implement this method
        return False