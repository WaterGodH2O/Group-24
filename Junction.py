from Arm import Arm
from Box import Box
import Lane
import Vehicle
from typing import List
from exceptions import TooManyVehiclesException
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

    def __init__(self,
                 traffic_data: list[list[int]],
                 traffic_light_interval_ms: int = 20000,
                 num_lanes: int = 2,
                 pedestrian_crossing: bool = False,
                 p_crossing_time_s: int = 0,
                 p_crossing_freq: int = 0):
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
        self.traffic_data: list[list[int]] = [[0, 300, 200, 300], [250, 0, 400, 200], [2000, 120, 0, 150], [0, 0, 30, 0]]
        #Precompute scale values for exponential random distribution
        self.traffic_scales: list[list[int]] = [[(60*60*1000)/val if val != 0 else 0 for val in row ] for row in self.traffic_data]
        
        self.num_lanes: int = num_lanes
        self.pedestrian_crossing: bool = pedestrian_crossing
        #Initialise time between vehicle creation to 0 for all pairs of sources and destinations
        self.vehicle_timers_ms:int = np.zeros((self.NUM_ARMS, self.NUM_ARMS))
        
        #Initialise traffic light to north
        self.traffic_light_dir: int = 0
        #Set the interval between changes and the traffic light timer to the given interval
        self.traffic_light_time_ms: int = traffic_light_interval_ms
        self.traffic_light_interval_ms: int = traffic_light_interval_ms
        #Initialise timer for the interval between one light turning red and another turning green.
        self.traffic_light_gap_timer_ms: int = 0
        #Initialise value to store the light direction before pedestrian crossings and light changes
        self.prev_light_dir: int = 0
        self.p_crossing = pedestrian_crossing
        if(pedestrian_crossing):
            #Calculate the scale value and take a sample for the initial time
            self.p_crossing_scale: int = 60*60*1000/p_crossing_freq
            self.p_crossing_interval_time_ms = self.random.exponential(self.p_crossing_scale)

        #Initialise p_crossing_queued, which is called by update_traffic_light so must always be set
        self.p_crossing_queued = False
        #Initialise the length of the crossing cycle and the timer to track it.
        self.p_crossing_length_ms = p_crossing_time_s * 1000
        self.p_crossing_timer_ms = 0

        #used to test car generation
        self.cars_made = np.zeros((self.NUM_ARMS, self.NUM_ARMS))

        self.arms: List[Arm] = [
            Arm(self.LANE_WIDTH * num_lanes, self.LANE_LENGTH, self.traffic_data[i], self.num_lanes)
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
                f"  Pedestrian crossing: {'Yes' if self.pedestrian_crossing else 'No'}\n")

    
    def get_kpi(self) -> List[List[int]]:
        """ return the efficiency score, avg wait time, max wait time and max queue length for each arm of the junction """
        kpi_list = [arm.get_kpi() for arm in self.arms]
        return kpi_list
    
    def get_junction_information(self):
        """ method to return all configuration details about this particular junction """
        pass
    

    def simulate(self, sim_time_ms: int, update_length_ms: int):
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
        try:
            while (sim_time_ms > 0):
                
                    sim_time_ms -= update_length_ms
                    self.update(update_length_ms)
        except TooManyVehiclesException:
            print("Too many vehicles created in an arm, exiting early")
        #Show cars created
        np.set_printoptions(suppress=True)
        print(self.cars_made)
        print("Simulation finished")
        print(f"{self.box.vt} vehicles passed through out of {np.sum(self.cars_made)}")
    
    
    def update(self, update_length_ms: int) -> None:
        """
        Process one simulation step for thejunction.

        :param update_length_ms: The length of the simulation step in milliseconds
        """
        
        self.create_new_vehicles(update_length_ms)
        self.update_traffic_light(update_length_ms)
        if (self.p_crossing):
            self.update_pedestrian_crossing(update_length_ms)
        self.box.move_all_vehicles(update_length_ms)
        for i, arm in enumerate(self.arms):
            green_light = i == self.traffic_light_dir
            arm.move_all_vehicles(0, green_light, self.box, update_length_ms, self.NUM_ARMS)
    
    def update_traffic_light(self, update_length_ms: int) -> None:
        """
        Process one simulation step for the traffic light.

        :param update_length_ms: The length of the simulation step in milliseconds
        """
        #Branch depending on if the light is currently in a gap between changes or not.
        if self.traffic_light_gap_timer_ms <= 0:
            self.update_traffic_light_green(update_length_ms)
        #If p_crossing_timer > 0, then the pedestrian crossing is active and lights are handled by that.
        elif self.p_crossing_timer_ms <= 0:
            self.update_traffic_light_all_red(update_length_ms)

        #Test print for light timing
        #print(f"Current light direction: {self.traffic_light_dir}\nCurrent light timer: {self.traffic_light_time_ms}\nGap timer: {self.traffic_light_gap_timer_ms}")

    def update_traffic_light_green(self, update_length_ms: int) -> None:
        """ Process one traffic light step when one of the lights is green"""
        #Subtract the length of the update from the timer
        self.traffic_light_time_ms -= update_length_ms

        #If no cars are within 100m of the light, the time is below 0 or a crossing cycle is queued, set all lights red and start the gap timer
        if self.arms[self.traffic_light_dir].no_vehicles_within(100) or self.traffic_light_time_ms <= 0:       
            self.traffic_light_gap_timer_ms = self.TRAFFIC_LIGHT_GAP_MS
            self.prev_light_dir = self.traffic_light_dir
            self.traffic_light_dir = -1
            #print("Light changed to red")
    
    def update_traffic_light_all_red(self, update_length_ms: int) -> None:
        """ Process one traffic light update when in between light cycles when no pedestrian crossing is active """
        #Subtract the length of the update
        self.traffic_light_gap_timer_ms -= update_length_ms

        #At the end of the gap, reset the main interval and update the direction
        if self.traffic_light_gap_timer_ms <= 0:
            self.traffic_light_time_ms = self.traffic_light_interval_ms
            #To update direction, check each direction clockwise for vehicles. If a vehicle is found, set that direction green. 
            #If none are found, set the first direction anticlockwise green
            self.traffic_light_dir = self.prev_light_dir
            for i in range(0,self.NUM_ARMS - 2):
                self.traffic_light_dir = self.get_left_arm(self.traffic_light_dir)
                if self.arms[self.traffic_light_dir].no_vehicles_within(100):
                    break
            #print("Light changed to green")
                

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
                    self.cars_made[source][dest] += 1
                    
                    self.arms[source].create_vehicle(self.VEHICLE_SPEED_MPS, source, dest, "Car")

    def update_pedestrian_crossing(self, update_length_ms: int) -> None:
        #Crossing active
        if (self.p_crossing_timer_ms > 0):
            #Decrement timer.
            self.p_crossing_timer_ms -= update_length_ms
            #When timer reaches 0, remove the crossing request.
            #update_traffic_light will now proceed with the traffic light gap
            if (self.p_crossing_timer_ms <= 0):
                self.p_crossing_queued = False
            #print(f"Pedestrian crossing time left: {self.p_crossing_timer_ms}")
        #Crossing queued, not currently active and at the start of a traffic light gap
        elif (self.p_crossing_queued and self.traffic_light_gap_timer_ms == self.TRAFFIC_LIGHT_GAP_MS):
            #Start the crossing
            self.p_crossing_timer_ms = self.p_crossing_length_ms
            #print(f"Pedestrian crossing started")
        #If crossing inactive and either not queued or not at the start of a light cycle
        else:
            #Decrease interval timer.
            self.p_crossing_interval_time_ms -= update_length_ms
            #If interval elapsed, queue a crossing and reset the time
            if (self.p_crossing_interval_time_ms <= 0):
                self.p_crossing_queued = True
                self.p_crossing_interval_time_ms = self.random.exponential(self.p_crossing_scale)
                #print("Crossing request received")
            #print(f"Crossing time: {self.p_crossing_interval_time_ms}, queued? {self.p_crossing_queued}")