from Arm import Arm
from Box import Box
from TrafficLight import TrafficLight
import Lane
import Vehicle
from typing import List
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
    queue_length_array: List[List[int]] = [[] * 4 for _ in range(4)]

    # the amount of time that should pass before we update the queue length
    queue_length_timer: int = 0

    def __init__(self,
                 traffic_data: list[list[int]],
                 traffic_light_interval_ms: int = 20000,
                 num_lanes: int = 2,
                 pedestrian_crossing: bool = False,
                 p_crossing_time_s: int = 0,
                 p_crossing_freq: int = 0,
                 bus_lane: bool = False,
                 bus_ratio: float = 0,
                 left_turn_lanes: bool = False):
        """
        初始化交通路口信息
        :param traffic_data: The number of vehicles per hour from each arm to another. The first index is the source arm and the second is the destination, numbered clockwise from north.

        :param num_lanes: number of lanes per arm and direction.
        :param pedestrian_crossing: if the crossing road applied
        :param simulation_duration: 模拟时间
        """
        #Initialise random number generator
        self.random = np.random.default_rng()
        #dummy data
        self.traffic_data = traffic_data
        #Precompute scale values for exponential random distribution
        self.traffic_scales: list[list[int]] = [[(60*60*1000)/val if val != 0 else 0 for val in row ] for row in self.traffic_data]
        
        self.num_lanes: int = num_lanes
        #Initialise time between vehicle creation to 0 for all pairs of sources and destinations
        self.vehicle_timers_ms:int = np.zeros((self.NUM_ARMS, self.NUM_ARMS))

        #Initialise traffic light
        self.traffic_light = TrafficLight(self.NUM_ARMS, 
                                          traffic_light_interval_ms,
                                          self.TRAFFIC_LIGHT_GAP_MS, 
                                          pedestrian_crossing,
                                          p_crossing_time_s,
                                          p_crossing_freq,
                                          self.random)
        
        #Initialise bus lanes
        self.bus_lanes = bus_lane
        self.bus_ratio = bus_ratio / 100

        #Initialise left turn lanes
        self.left_turn_lanes = left_turn_lanes

        #used to test car generation
        self.cars_made = np.zeros((self.NUM_ARMS, self.NUM_ARMS))
        self.arms: List[Arm] = [
            Arm(self.LANE_WIDTH * num_lanes, 
                self.LANE_LENGTH, self.traffic_data[i], 
                self.num_lanes, self.NUM_ARMS,
                self.bus_lanes, self.left_turn_lanes)
            for i in range (4)
        ]
        self.box = Box(self.LANE_WIDTH, self.num_lanes)


    def __str__(self):
        """print the detail information instead of memory address"""
        return (f"Junction Configuration:\n"
                f"Traffic Flow (vph):\n"
                f"  {self.traffic_data}\n"
                f"Configurable Parameters:\n"
                f"  Number of lanes: {self.num_lanes}\n"
                f"  Pedestrian crossing: {'Yes' if self.traffic_light.p_crossing else 'No'}\n"
                f"  Bus Lanes: {'Yes' if self.bus_lanes else 'No'}, ratio {self.bus_ratio}")

    
    def get_kpi(self) -> List[List[int]]:
        """ return the efficiency score, avg wait time, max wait time and max queue length for each arm of the junction """
        kpi_list = [arm.get_kpi() for arm in self.arms]
        return kpi_list

    def get_total_car_count(self) -> List[int]:
        """Retruns a list of the total throughput for each arm of the junction"""
        junction_throughput = [arm.get_total_car_count() for arm in self.arms]
        return junction_throughput
    
    def get_junction_information(self):
        """ method to return all configuration details about this particular junction """
        pass
    

    def simulate(self, sim_time_ms: int, update_length_ms: int) -> None:
        """
        Simulate the junction for a given period of time and at a given precision.

        :param sim_time_ms: The total length of time to simulate in milliseconds.
        :param update_length_ms: The length of each simulation step in milliseconds.
        """
        #Collision test
        """
        self.arms[0]._lanes[0]._vehicles.append(Vehicle.Car(18, 0, 3, 2))
        self.arms[0]._lanes[1]._vehicles.append(Vehicle.Car(18, 0, 2, 0))
        self.arms[0]._lanes[2]._vehicles.append(Vehicle.Car(18, 0, 1, 2))
        """
        
        # configure intervals to wait until we track queue count data
        self.queue_length_timer = sim_time_ms / 10

        try:
            while (sim_time_ms > 0):
                sim_time_ms -= update_length_ms
                self.update(update_length_ms)
                
                # store the current longest queue count for each arm
                if sim_time_ms % self.queue_length_timer == 0:
                    for i, arm in enumerate(self.arms):
                        current_queue_length = arm.get_current_queue_length()
                        self.queue_length_array[i].append(current_queue_length)

        except TooManyVehiclesException:
            print("Too many vehicles created in an arm, exiting early")
        #Show cars created
        np.set_printoptions(suppress=True)
        print(self.cars_made)
        print("Simulation finished")
        print(f"{self.box.vt} vehicles passed through out of {round(np.sum(self.cars_made))}")
    
    
    def update(self, update_length_ms: int) -> None:
        """
        Process one simulation step for thejunction.

        :param update_length_ms: The length of the simulation step in milliseconds
        """
        
        self.create_new_vehicles(update_length_ms)
        self.traffic_light.update_traffic_light(update_length_ms, self.arms)

        self.box.move_all_vehicles(update_length_ms)
        for i, arm in enumerate(self.arms):
            arm.move_all_vehicles(0, self.traffic_light._traffic_light_dir, self.box, update_length_ms, i)
    

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
                    self.cars_made[source][dest] += 1
                    #Create buses if a random number is less than the bus ratio
                    if self.random.uniform(0, 1) < self.bus_ratio:
                        self.arms[source].create_vehicle(self.VEHICLE_SPEED_MPS, source, dest, "Bus")
                    else:
                        self.arms[source].create_vehicle(self.VEHICLE_SPEED_MPS, source, dest, "Car")
