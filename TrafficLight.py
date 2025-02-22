from Arm import Arm
from numpy import random as Random
class TrafficLight:
    def __init__(self, num_arms: int,
                 traffic_light_interval_ms: int,
                 traffic_light_gap_ms: int,
                 pedestrian_crossing: bool, 
                 p_crossing_time_s: int,
                 p_crossing_freq: int,
                 random: Random
                 ):
        #Copy random number generator from junction
        self.random: Random = random
        #Initialise traffic light to north
        self.traffic_light_dir: int = 0
        #Set the interval between changes and the traffic light timer to the given interval
        self.traffic_light_time_ms: int = traffic_light_interval_ms
        self.traffic_light_interval_ms: int = traffic_light_interval_ms
        #Initialise timer for the interval between one light turning red and another turning green.
        self.traffic_light_gap_timer_ms: int = 0
        self.traffic_light_gap_ms: int = traffic_light_gap_ms
        #Initialise value to store the light direction before pedestrian crossings and light changes
        self.prev_light_dir: int = 0
        self.p_crossing: bool = pedestrian_crossing
        if pedestrian_crossing:
            #Calculate the scale value and take a sample for the initial time
            self.p_crossing_scale: int = 60*60*1000/p_crossing_freq
            self.p_crossing_interval_time_ms: float = self.random.exponential(self.p_crossing_scale)
            self.p_crossing_length_ms: int = p_crossing_time_s * 1000
            #Initialise the timer for crossings
            self.p_crossing_timer_ms: int = 0
            #Initialise p_crossing_queued, which is called by update_traffic_light so must always be set
            self.p_crossing_queued: bool = False
        self.num_arms: int = num_arms

    def update_traffic_light(self, update_length_ms: int, arms: list[Arm]) -> None:
        """
        Process one simulation step for the traffic light.

        :param update_length_ms: The length of the simulation step in milliseconds
        """
        #Branch depending on if the light is currently in a gap between changes or not.
        if self.traffic_light_gap_timer_ms <= 0:
            self.update_traffic_light_green(update_length_ms, arms)
        else:
            #If pedestrian crossings are enabled, only do the all_red update if the pedestrian crossing is not active
            if self.p_crossing:
                if self.p_crossing_timer_ms <= 0:
                    self.update_traffic_light_all_red(update_length_ms, arms)
            else:
                self.update_traffic_light_all_red(update_length_ms, arms)

        #If pedestrian crossings are enabled, update them every time
        if self.p_crossing:
            self.update_pedestrian_crossing(update_length_ms)

        #Test print for light timing
        #print(f"Current light direction: {self.traffic_light_dir}\nCurrent light timer: {self.traffic_light_time_ms}\nGap timer: {self.traffic_light_gap_timer_ms}")

    def update_traffic_light_green(self, update_length_ms: int, arms: list[Arm]) -> None:
        """ Process one traffic light step when one of the lights is green"""
        #Subtract the length of the update from the timer
        self.traffic_light_time_ms -= update_length_ms

        #If no cars are within 100m of the light, the time is below 0, set all lights red and start the gap timer
        if arms[self._traffic_light_dir].no_vehicles_within(100) or self.traffic_light_time_ms <= 0:       
            self.traffic_light_gap_timer_ms = self.traffic_light_gap_ms
            self.prev_light_dir = self._traffic_light_dir
            self._traffic_light_dir = -1
            #print("Light changed to red")
    
    def update_traffic_light_all_red(self, update_length_ms: int, arms: list[Arm]) -> None:
        """ Process one traffic light update when in between light cycles when no pedestrian crossing is active """
        #Subtract the length of the update
        self.traffic_light_gap_timer_ms -= update_length_ms

        #At the end of the gap, reset the main interval and update the direction
        if self.traffic_light_gap_timer_ms <= 0:
            self.traffic_light_time_ms = self.traffic_light_interval_ms
            #To update direction, check each direction clockwise for vehicles. If a vehicle is found, set that direction green. 
            #If none are found, set the first direction anticlockwise green
            self._traffic_light_dir = self.prev_light_dir
            for i in range(0,self.num_arms - 1):
                self._traffic_light_dir = self.get_left_arm(self._traffic_light_dir)
                if not arms[self._traffic_light_dir].no_vehicles_within(100):
                    break
            #print(f"Light changed to green, direction {self.traffic_light_dir}")
    
    def update_pedestrian_crossing(self, update_length_ms: int) -> None:
        #Crossing active
        if (self.p_crossing_timer_ms > 0):
            #Decrement timer.
            self.p_crossing_timer_ms -= update_length_ms
            #When timer reaches 0, remove the crossing request.
            #update_traffic_light will now proceed with the traffic light gap
            if (self.p_crossing_timer_ms <= 0):
                self.p_crossing_queued = False
                #print("Pedestrian crossing ended")
            #print(f"Pedestrian crossing time left: {self.p_crossing_timer_ms}")
        #Crossing queued, not currently active and at the start of a traffic light gap
        elif (self.p_crossing_queued and self.traffic_light_gap_timer_ms == self.traffic_light_gap_ms):
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

    def get_left_arm(self, arm_index: int) -> int:
        """ Get the index in arms of the arm clockwise to the given index"""
        return (arm_index + 1) % self.num_arms
    
    def get_right_arm(self, arm_index: int) -> int:
        """ Get the index in arms of the arm anti-clockwise to the given index"""
        return (arm_index - 1) % self.num_arms