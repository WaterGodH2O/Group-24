from abc import ABC, abstractmethod

import Vehicle


class Lane(ABC):
    """
    The abstract class Lane, which defines the basic interface for all lanes.
    """
    @property
    @abstractmethod
    def lane_type(self):
        pass

    @property
    @abstractmethod
    # contain all the instance of car which is in the lane
    def car_list(self):
        pass

    @abstractmethod
    def add_vehicle(self, vehicle: Vehicle):
        pass

    @abstractmethod
    def remove_vehicle(self, vehicle: Vehicle):
        pass

    @property
    @abstractmethod
    # indicate whether the vehicle in this lane are allowed to enter junction
    # i.e. whether cooresponding traffic light is green.
    def allow_enter_junction(self) -> bool:
        pass


class CarLane(Lane):
    def __init__(self):
        self.car_list = []

    def add_vehicle(self, vehicle: Vehicle):
        self.car_list.append(vehicle)

    def remove_vehicle(self, vehicle: Vehicle):
        self.car_list.remove(vehicle)

    def calculate_flow(self):
        return len(self.car_list)

class BusLane(Lane):

    def __init__(self):
        self.car_list = []

    def add_vehicle(self, vehicle: Vehicle):
        # if this vehicle is the bus

        self.car_list.append(vehicle)

    def remove_vehicle(self, vehicle: Vehicle):
        self.car_list.remove(vehicle)

    def calculate_flow(self):
        return len(self.car_list)