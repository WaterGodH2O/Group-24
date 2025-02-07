from Arm import Arm
from Box import Box
import Lane
import Vehicle
from typing import List
import numpy as np

class Junction:
    #Assume lanes are 3m wide, 500m long
    LANE_WIDTH: int = 3
    LANE_LENGTH: int = 500

    NUM_ARMS: int = 4
    #40 miles per hour is approximately 18 metres per second
    VEHICLE_SPEED_MPS: int = 18

    def __init__(self,
                 traffic_data: list[list[int]],
                 traffic_light_interval_ms: int = 20000,
                 num_lanes: int = 2,
                 pedestrian_crossing: bool = False):
        """
        初始化交通路口信息
        :param traffic_data: The number of vehicles per hour from each arm to another. The first index is the source arm and the second is the destination, numbered clockwise from north.

        :param num_lanes: number of lanes per arm and direction.
        :param pedestrian_crossing: if the crossing road applied
        :param simulation_duration: 模拟时间
        """
        #Initialise random number generator
        self.random = np.random.default_rng()

        self.traffic_data: list[list[int]] = [[0, 100, 200, 3000], [250, 0, 1, 2], [20, 20, 0, 20], [1, 0, 3, 0]]
        #Precompute scale values for exponential random distribution
        self.traffic_scales: list[list[int]] = [[(60*60*1000)/val if val != 0 else 0 for val in row ] for row in self.traffic_data]
        
        self.num_lanes: int = num_lanes
        self.pedestrian_crossing: bool = pedestrian_crossing

        #Initialise traffic light to north
        self.traffic_light_dir: int = 0
        #Set the interval between changes and the traffic light timer to the given interval
        self.traffic_light_time_ms: int = traffic_light_interval_ms
        self.traffic_light_interval_ms: int = traffic_light_interval_ms

        #Initialise time between vehicle creation to 0 for all pairs of sources and destinations
        self.vehicle_timers_ms:int = np.zeros((self.NUM_ARMS, self.NUM_ARMS))

        self.arms: List[Arm] = [None]*self.NUM_ARMS
        for i in range(len(self.arms)):
            self.arms[i] = Arm(self.LANE_WIDTH * num_lanes, self.LANE_LENGTH, self.traffic_data[i], self.num_lanes)
        self.box: Box = Box(self.LANE_WIDTH, self.num_lanes)


    def __str__(self):
        """print the detail information instead of memory address"""
        return (f"Junction Configuration:\n"
                f"Traffic Flow (vph):\n"
                f"  {self.traffic_data}\n"
                f"Configurable Parameters:\n"
                f"  Number of lanes: {self.num_lanes}\n"
                f"  Pedestrian crossing: {'Yes' if self.pedestrian_crossing else 'No'}\n")
    

    def simulate(self, sim_time_ms: int, update_length_ms: int) -> None:
        """
        Simulate the junction for a given period of time and at a given precision.

        :param sim_time_ms: The total length of time to simulate in milliseconds.
        :param update_length_ms: The length of each simulation step in milliseconds.
        """
        while (sim_time_ms > 0):
            sim_time_ms -= update_length_ms
            self.update(update_length_ms)

        print("Simulation finished")
    
    
    def update(self, update_length_ms: int) -> None:
        """
        Process one simulation step for thejunction.

        :param update_length_ms: The length of the simulation step in milliseconds
        """
        self.create_new_vehicles(update_length_ms)
        self.update_traffic_light(update_length_ms)
    
    def update_traffic_light(self, update_length_ms: int) -> None:
        """
        Process one simulation step for the traffic light.

        :param update_length_ms: The length of the simulation step in milliseconds
        """
        #Subtract the length of the update from the timer
        self.traffic_light_time_ms -= update_length_ms

        #If no cars are within 100m of the light or the time is below 0, skip the direction and reset the interval
        if self.arms[self.traffic_light_dir].no_vehicles_within(100) or self.traffic_light_time_ms <= 0:       
            self.traffic_light_dir = self.get_left_arm(self.traffic_light_dir)
            self.traffic_light_time_ms = self.traffic_light_interval_ms


    def get_left_arm(self, arm_index: int) -> int:
        """ Get the index in arms of the arm clockwise to the given index"""
        return (arm_index + 1) % self.NUM_ARMS
    
    def get_right_arm(self, arm_index: int) -> int:
        """ Get the index in arms of the arm anti-clockwise to the given index"""
        return (arm_index - 1) % self.NUM_ARMS

    def create_new_vehicles(self, update_length_ms: int) -> None:
        """
        Attempt to create new vehicles
        """
        for source in range(0, self.NUM_ARMS):
            for dest in range(0, self.NUM_ARMS):
                #If an entry has no vehicles, skip it
                if (self.traffic_data[source][dest] == 0):
                    continue
                #Decrement the timer by the length of the update
                self.vehicle_timers_ms[source][dest] -= update_length_ms

                #If a timer is less than 0, create a car and increment the timer by a random value.
                #If the timer is still below 0, multiple cars are created in a single update.
                while(self.vehicle_timers_ms[source][dest] <= 0):
                    time_to_next_ms = self.random.exponential(self.traffic_scales[source][dest])
                    self.vehicle_timers_ms[source][dest] += time_to_next_ms
                    #TODO: create vehicle