from Vehicle import Vehicle

class Box:
    def __init__(self, 
                 lane_width: int, 
                 maximum_lane_count: int):
        self._vehicles: list[Vehicle] = list()
        """
        The size of the junction is equal to the width of each lane times the maximum number of lanes
        in a given arm.
        """
        self._size = lane_width * maximum_lane_count * 2
        self.vt = 0

    def add_vehicle(self, vehicle: Vehicle) -> None:
        """Add a new vehicle to the box adding the box size to its distance and adding it to the list"""
        vehicle.set_position(self._size + vehicle.distance)
        self._vehicles.append(vehicle)

    def move_all_vehicles(self, update_length_ms: int) -> None:
        vehicles_to_delete: list[Vehicle] = []
        for vehicle in self._vehicles:
            vehicle.set_position(vehicle.get_next_position(update_length_ms))
            if (vehicle.distance <= 0):
                vehicles_to_delete.append(vehicle)
                self.vt += 1
        if len(vehicles_to_delete) != 0:
            #Remove all vehicles have distances below 0
            self._vehicles = [v for v in self._vehicles if v not in vehicles_to_delete]


    def get_vehicles(self) -> list[Vehicle]:
        return self._vehicles