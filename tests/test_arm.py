from unittest.mock import MagicMock
from Arm import Arm
from Lane import Lane
from Vehicle import Vehicle
import unittest

class TestArm(unittest.TestCase):
    def setUp(self):
        self.arm = Arm(2, 100, [20, 30, 40, 0], 3)

    def test_get_kpi(self):
        """ ensure that the correct kpi details are returned """
        # mock some kpi variables
        self.arm._total_wait_times = 30
        self.arm._total_car_count = 6
        self.arm._max_wait_time = 10
        self.arm._max_queue_length = 4

        # ensure that the get kpi method returns the correct values
        self.assertEqual(self.arm.get_kpi(), [19, 5, 10, 4])

    def test_move_all_vehicles(self):
        # create some mock lanes
        lane1 = MagicMock(spec=Lane)
        lane2 = MagicMock(spec=Lane)
        lane3 = MagicMock(spec=Lane)

        # mock the lane length
        lane1.length = 4
        lane2.length = 2
        lane3.length = 6

        # create mock cars for lanes 1 and 3 to return
        car1 = MagicMock(spec=Vehicle)
        car3 = MagicMock(spec=Vehicle)
        
        # mock the vehicle arrival times
        car1.arrival_time = 1000 # arrived at 1s
        car3.arrival_time = 4000 # arrived at 4s

        # update the lane.move_all_vehicles return value for each lane to car1, None and car3 respectively
        lane1.move_all_vehicles.return_value = car1
        lane2.move_all_vehicles.return_value = None
        lane3.move_all_vehicles.return_value = car3

        # configure the arm
        self.arm._lanes = [lane1, lane2, lane3]
        self.arm._total_car_count = 2 # 2 vehicles
        self.arm._total_wait_times = 3 # 3 seconds
        self.arm._max_wait_time = 2 # 2 seconds
        self.arm._max_queue_length = 5 # 5 vehicles
        
        # call move_all_vehicles
        self.arm.move_all_vehicles(7000, True)

        # assert that the kpi values have been updated as intended
        self.assertEqual(self.arm._total_car_count, 4)
        self.assertEqual(self.arm._total_wait_times, 12)
        self.assertEqual(self.arm._max_wait_time, 6)
        self.assertEqual(self.arm._max_queue_length, 6)
        

