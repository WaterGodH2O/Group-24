import Vehicle

class Box:
    def __init__(self, lane_width, maximum_lane_count):
        self.Vehicles = list()
        """
        The size of the junction is equal to the width of each lane times the maximum number of lanes
        in a given arm.
        """
        self.size = lane_width * maximum_lane_count