from abc import ABC, abstractmethod

class Lane(ABC):
    @property
    @abstractmethod
    def lane_type(self):
        pass

    @property
    @abstractmethod
    def car_num(self):
        pass

class CarLane(Lane):
    lane_type = "Car"

    def __init__(self, max_speed):
        self._max_speed = max_speed

    @property
    def max_speed(self):
        return self._max_speed

class BikeLane(Lane):
    lane_type = "Bike"

    def __init__(self, max_speed):
        self._max_speed = max_speed

    @property
    def max_speed(self):
        return self._max_speed

# 测试代码
car_lane = CarLane(60)
bike_lane = BikeLane(20)
