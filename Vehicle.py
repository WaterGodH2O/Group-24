from abc import ABC, abstractmethod

class Vehicle(ABC):
    @property
    @abstractmethod
    def vehicle_type(self):
        pass

    @property
    @abstractmethod
    def x(self):
        pass

    @property
    @abstractmethod
    def y(self):
        pass

    @property
    @abstractmethod
    # the waiting time of vehicle in the lane
    def age(self):
        pass

class Car(Vehicle):
    def __init__(self, x, y):
        self._x = x
        self._y = y
        self.vehicle_type = "Car"

    @property
    def vehicle_type(self):
        return self.vehicle_type

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

class Bus(Vehicle):
    def __init__(self, x, y):
        self._x = x
        self._y = y
        self.vehicle_type = "Bus"

    @property
    def vehicle_type(self):
        return self.vehicle_type
    @property
    def x(self):
        return self._x
    @property
    def y(self):
        return self._y
