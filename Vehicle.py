from abc import ABC, abstractmethod
import Arm
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
        self._waiting_time = 0

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
    def waiting_time(self):
        return self._waiting_time
    
    def moveArm(self, arm: Arm, timems: int):
        #Get the distance of the next car in the lane plus the stopping distance, or 0 if there are no cars ahead
        target_position = 0 or (arm.get_lane(self._source).get_vehicle_ahead().distance + self._stopping_distance)
        #Subtract the distance travelled in a single tick, or set to the target position if that is greater
        self._distance = max(target_position, self._distance - timems * self._speed / 1000)

        #TODO: lane changes

        #TODO: enter junction


        

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


