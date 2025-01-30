class Junction:
    def __init__(self,
                 e2n: int = 0, e2s: int = 0, e2w: int = 0,
                 w2n: int = 0, w2s: int = 0, w2e: int = 0,
                 n2e: int = 0, n2s: int = 0, n2w: int = 0,
                 s2e: int = 0, s2n: int = 0, s2w: int = 0,
                 num_lanes: int = 2,
                 pedestrian_crossing: bool = False,
                 simulation_duration: int = 120):
        """
        初始化交通路口信息
        :param e2n: The VPH of from East to North（vph）
        :param e2s: The VPH of from East to South（vph）

        :param num_lanes: 车道数（2-4）
        :param pedestrian_crossing: 是否有行人过道
        :param simulation_duration: 模拟时间
        """

        self.e2n = e2n
        self.e2s = e2s
        self.e2w = e2w
        self.w2n = w2n
        self.w2s = w2s
        self.w2e = w2e
        self.n2e = n2e
        self.n2s = n2s
        self.n2w = n2w
        self.s2e = s2e
        self.s2n = s2n
        self.s2w = s2w


        self.num_lanes = num_lanes
        self.pedestrian_crossing = pedestrian_crossing
        self.simulation_duration = simulation_duration

    def __str__(self):
        """print the detail information instead of memory address"""
        return (f"Junction Configuration:\n"
                f"Traffic Flow (vph):\n"
                f"  East->North: {self.e2n}, East->South: {self.e2s}, East->West: {self.e2w}\n"
                f"  West->North: {self.w2n}, West->South: {self.w2s}, West->East: {self.w2e}\n"
                f"  North->East: {self.n2e}, North->South: {self.n2s}, North->West: {self.n2w}\n"
                f"  South->East: {self.s2e}, South->North: {self.s2n}, South->West: {self.s2w}\n"
                f"Configurable Parameters:\n"
                f"  Number of lanes: {self.num_lanes}\n"
                f"  Pedestrian crossing: {'Yes' if self.pedestrian_crossing else 'No'}\n"
                f"  Crossing time: {self.crossing_time} seconds\n"
                f"  Crossing request frequency: {self.crossing_frequency} per hour\n"
                f"  Simulation duration: {self.simulation_duration} minutes\n")