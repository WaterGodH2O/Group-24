from abc import ABC, abstractmethod
import time

class Vehicle(ABC):
    def __init__(self, vehicle_type: str, length: float, speed: int, source: int, destination: int, start_position: float):
        #Arm ID of the vehicle's start and end
        self._source = source
        self._destination = destination
        #Distance from the traffic light
        self._distance = start_position
        #Length of the vehicle in metres
        self._length = length
        #Minimum distance between this vehicle and the next
        self._stopping_distance = length / 2
        #Speed in metres per second
        self._speed = speed
        self._vehicle_type = vehicle_type
        #Time spent waiting in milliseconds
        self._arrival_time = time.time()

    @property
    def vehicle_type(self):
        return self._vehicle_type

    @property
    def source(self):
        return self._source
    @property
    def distance(self):
        return self._distance
    @property
    def destination(self):
        return self._destination

    @property
    def arrival_time(self):
        return self._arrival_time

class Car(Vehicle):
    def __init__(self, speed, source, destination, start_position):
        #Cars are on average 4.4m long in the UK
        CAR_LENGTH = 4.4
        super().__init__("Car", CAR_LENGTH, speed, source, destination, start_position)


class Bus(Vehicle):
    def __init__(self, speed, source, destination, start_position):
        #Busses are typically 9 to 11m long
        BUS_LENGTH = 10
        super().__init__("Bus", BUS_LENGTH, speed, source, destination, start_position)


