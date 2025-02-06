from Arm import Arm
from Box import Box
from typing import List
import numpy as np

class Junction:
    #Assume lanes are 3m wide, 500m long
    LANE_WIDTH: int = 3
    LANE_LENGTH: int = 500

    def __init__(self,
                 traffic_data: list[list[int]],
                 num_lanes: int = 2,
                 pedestrian_crossing: bool = False,
                 simulation_duration: int = 120):
        """
        初始化交通路口信息
        :param traffic_data: The number of vehicles per hour from each arm to another. The first index is the source arm and the second is the destination, numbered clockwise from north.

        :param num_lanes: number of lanes per arm and direction.
        :param pedestrian_crossing: if the crossing road applied
        :param simulation_duration: 模拟时间
        """

        self.traffic_data = np.zeros((4,4))
        
        self.num_lanes = num_lanes
        self.pedestrian_crossing = pedestrian_crossing
        self.simulation_duration = simulation_duration

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
                f"  Pedestrian crossing: {'Yes' if self.pedestrian_crossing else 'No'}\n"
                f"  Simulation duration: {self.simulation_duration} minutes\n")
    
    def simulate(self) -> int:
        # dummy score
        return self.num_lanes*20
    
    def get_kpi(self) -> List[List[int]]:
        """ return the efficiency score, avg wait time, max wait time and max queue length for each arm of the junction """
        kpi_list = [arm.get_kpi() for arm in self.arms]
        return kpi_list
    
    def get_junction_information(self):
        """ method to return all configuration details about this particular junction """
        pass
