from Arm import Arm
from Box import Box
from TrafficLight import TrafficLight
import Lane
import Vehicle
from typing import List, Set
from exceptions import TooManyVehiclesException, NotEnoughLanesException
import numpy as np

class Junction:
    #Assume lanes are 3m wide, 10000m long (length is to halt early if the junction cannot handle throughput)
    LANE_WIDTH: int = 3
    LANE_LENGTH: int = 10000
    NUM_ARMS: int = 4
    #40 miles per hour is approximately 18 metres per second
    VEHICLE_SPEED_MPS: int = 18

    #Time between one traffic light turning off and another turning on
    #Set to 5s (2s all red time, 3s red+amber for next direction)
    TRAFFIC_LIGHT_GAP_MS: int = 5000

    # stores the max queue length at given intervals of the simulation for each arm
    _queue_length_array: List[List[int]] = [[] * 4 for _ in range(4)]

    # the amount of time that should pass before we update the queue length
    _queue_length_timer: int = 0

    def __init__(self,
                 traffic_data: list[list[int]],
                 allowed_lane_directions: List[Set[int]] = None,
                 traffic_light_interval_ms: int = 20000,
                 num_lanes: int = 2,
                 pedestrian_crossing: bool = False,
                 p_crossing_time_s: int = 0,
                 p_crossing_freq: float = 0,
                 bus_lane: bool = False,
                 bus_ratio: float = 0,
                 left_turn_lanes: bool = False):
        """
        Initialise junction
        :param traffic_data: The number of vehicles per hour from each arm to another. The first index is the source arm and the second is the destination, numbered clockwise from north.
        :param num_lanes: number of lanes per arm and direction.
        :param pedestrian_crossing: True if a pedestrian crossing is present, false otherwise
        """
        #If no lane directions are given, allow all directions
        if allowed_lane_directions == None:
            allowed_lane_directions = [{i for i in range(self.NUM_ARMS)} for _ in range(num_lanes)]
        #Initialise random number generator
        self._random = np.random.default_rng()
        #Initialise traffic data
        self._traffic_data = traffic_data
        #Precompute scale values for exponential random distribution
        self._traffic_scales: list[list[int]] = [[(60*60*1000)/val if val != 0 else 0 for val in row ] for row in self._traffic_data]
        #Initialise number and directions of lanes
        self._num_lanes: int = num_lanes
        self._allowed_lane_directions = allowed_lane_directions
        #Initialise time between vehicle creation to 0 for all pairs of sources and destinations
        self._vehicle_timers_ms:int = np.zeros((self.NUM_ARMS, self.NUM_ARMS))

        #Initialise traffic light
        self._traffic_light = TrafficLight(self.NUM_ARMS, 
                                          traffic_light_interval_ms,
                                          self.TRAFFIC_LIGHT_GAP_MS, 
                                          pedestrian_crossing,
                                          p_crossing_time_s,
                                          p_crossing_freq,
                                          self._random)
        
        #Initialise bus lanes
        self._bus_lanes = bus_lane
        self._bus_ratio = bus_ratio / 100

        #Initialise left turn lanes
        self._left_turn_lanes = left_turn_lanes
        #Initialise junction components
        self._arms: List[Arm] = [
            Arm(self.LANE_WIDTH * num_lanes, 
                self.LANE_LENGTH, self._traffic_data[i], 
                self._num_lanes, self.NUM_ARMS,
                self._bus_lanes, self._left_turn_lanes,
                allowed_lane_directions
            )
            for i in range (4)
        ]
        self._box = Box(self.LANE_WIDTH, self._num_lanes)


    def __str__(self):
        """ Print detailed junction information """
        return (f"Junction Configuration:\n"
                f"Traffic Flow (vph):\n"
                f"  {self._traffic_data}\n"
                f"Configurable Parameters:\n"
                f"  Number of lanes: {self._num_lanes}\n"
                f"  Pedestrian crossing: {'Yes' if self._traffic_light.p_crossing else 'No'}\n"
                f"  Bus Lanes: {'Yes' if self._bus_lanes else 'No'}, ratio {self._bus_ratio}")

    
    def get_kpi(self) -> List[List[int]]:
        """ return the efficiency score, avg wait time, max wait time and max queue length for each arm of the junction """
        kpi_list = [arm.get_kpi() for arm in self._arms]
        return kpi_list

    def get_total_car_count(self) -> List[int]:
        """Retruns a list of the total throughput for each arm of the junction"""
        junction_throughput = [arm.get_total_car_count() for arm in self._arms]
        return junction_throughput
    
    def get_junction_information(self):
        """ method to return lane configuration details about this particular junction """
        return self._allowed_lane_directions
    
    def get_arm_throughputs(self):
        return self._box.get_arm_throughputs()
    

    def simulate(self, sim_time_ms: int, update_length_ms: int) -> None:
        """
        Simulate the junction for a given period of time and at a given precision.

        :param sim_time_ms: The total length of time to simulate in milliseconds.
        :param update_length_ms: The length of each simulation step in milliseconds.
        """
        
        # configure intervals to wait until we track queue count data
        self._queue_length_timer = sim_time_ms / 10

        try:
            while (sim_time_ms > 0):
                sim_time_ms -= update_length_ms
                self.update(update_length_ms)
                
                # store the current longest queue count for each arm
                if sim_time_ms % self._queue_length_timer == 0:
                    for i, arm in enumerate(self._arms):
                        current_queue_length = arm.get_current_queue_length()
                        self._queue_length_array[i].append(current_queue_length)

        except TooManyVehiclesException:
            print("Too many vehicles created in an arm, exiting early")
    
    
    def update(self, update_length_ms: int) -> None:
        """
        Process one simulation step for thejunction.

        :param update_length_ms: The length of the simulation step in milliseconds
        """
        
        self.create_new_vehicles(update_length_ms)
        self._traffic_light.update_traffic_light(update_length_ms, self._arms)
        self._box.move_all_vehicles(update_length_ms)
        for i, arm in enumerate(self._arms):
            arm.move_all_vehicles(0, self._traffic_light.traffic_light_dir, self._box, update_length_ms, i)
    

    def create_new_vehicles(self, update_length_ms: int) -> None:
        """
        Attempt to create new vehicles
        """
        for source in range(0, self.NUM_ARMS):
            for dest in range(0, self.NUM_ARMS):
                #If an entry has no vehicles, skip it
                if (self._traffic_data[source][dest] == 0):
                    continue
                #Decrement the timer by the length of the update
                self._vehicle_timers_ms[source][dest] -= update_length_ms

                #If a timer is less than 0, create a car and increment the timer by a random value.
                #If the timer is still below 0, multiple cars are created in a single update.
                while(self._vehicle_timers_ms[source][dest] <= 0):
                    time_to_next_ms = self._random.exponential(self._traffic_scales[source][dest])
                    self._vehicle_timers_ms[source][dest] += time_to_next_ms
                    #Create buses if a random number is less than the bus ratio
                    if self._random.uniform(0, 1) < self._bus_ratio:
                        self._arms[source].create_vehicle(self.VEHICLE_SPEED_MPS, source, dest, "Bus")
                    else:
                        self._arms[source].create_vehicle(self.VEHICLE_SPEED_MPS, source, dest, "Car")
