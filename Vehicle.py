from abc import ABC

class Vehicle(ABC):
    def __init__(self, vehicle_type: str, length: float, speed: int, source: int, destination: int, start_position: float, wait_time_ms: int):
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
        #How long a vehicle has been waiting at junction in milliseconds
        self._wait_time = 0
        #Lane vehicle came from. Set when entering box to calculate collisions.
        self._source_lane = None

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
    def wait_time(self):
        return self._wait_time
    
    @property
    def source_lane(self):
        return self._source_lane
    
    def set_position(self, position) -> None:
        self._distance = position

    def get_next_position(self, update_length_ms: int) -> int:
        #Calculate the new position of the vehicle after moving for the given time
        return self._distance - (self._speed * update_length_ms / 1000)
    
    def set_source_lane(self, source_lane: int) -> None:
        self._source_lane = source_lane

    def update_wait_time(self, update_length_ms: int):
        self._wait_time += update_length_ms

    def get_relative_direction(self, num_arms: int) -> int:
        """
        Returns the number of arms between the source and destination anticlockwise
        """
        return (self.source - self.destination) % num_arms
    

class Car(Vehicle):
    def __init__(self, speed, source, destination, start_position, wait_time_ms = 0):
        #Cars are on average 4.4m long in the UK
        CAR_LENGTH = 4.4
        super().__init__("Car", CAR_LENGTH, speed, source, destination, start_position, wait_time_ms)


class Bus(Vehicle):
    def __init__(self, speed, source, destination, start_position, wait_time_ms = 0):
        #Busses are typically 9 to 11m long
        BUS_LENGTH = 10
        super().__init__("Bus", BUS_LENGTH, speed, source, destination, start_position, wait_time_ms)


