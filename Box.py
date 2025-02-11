from Vehicle import Vehicle

class Box:
    def __init__(self, lane_width: int, maximum_lane_count: int):
        self._vehicles: list[Vehicle] = list()
        """
        The size of the junction is equal to the width of each lane times the maximum number of lanes
        in a given arm.
        """
        self._size = lane_width * maximum_lane_count * 2

    def addVehicle(self, vehicle: Vehicle) -> None:
        """Add a new vehicle to the box by resetting its position to 0 and adding it to the list"""
        vehicle.setPosition(self._size)
        self._vehicles.append(vehicle)

    def moveAllCars(self, update_length_ms: int) -> None:
        for vehicle in self._vehicles:
            vehicle.setPosition(vehicle.getNextPosition(update_length_ms))
            if (vehicle.distance <= 0):
                self._vehicles.remove(vehicle)