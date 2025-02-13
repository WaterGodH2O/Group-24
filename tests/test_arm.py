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
        self.assertEqual(self.arm.get_kpi(), [5, 10, 4])

    # def test_move_all_vehicles(self):
    #     # create some mock lanes
    #     lane1 = MagicMock(spec=Lane)
    #     lane2 = MagicMock(spec=Lane)
    #     lane3 = MagicMock(spec=Lane)

    #     # mock the lane length
    #     lane1.queue_length = 4
    #     lane2.queue_length = 2
    #     lane3.queue_length = 6

    #     # create mock cars for lanes 1 and 3 to return
    #     car1 = MagicMock(spec=Vehicle)
    #     car3 = MagicMock(spec=Vehicle)
        
    #     # mock the vehicle arrival times
    #     car1.arrival_time = 1000 # arrived at 1s
    #     car3.arrival_time = 4000 # arrived at 4s

    #     # update the lane.move_all_vehicles return value for each lane to car1, None and car3 respectively
    #     lane1.move_all_vehicles.return_value = car1
    #     lane2.move_all_vehicles.return_value = None
    #     lane3.move_all_vehicles.return_value = car3

    #     # configure the arm
    #     self.arm._lanes = [lane1, lane2, lane3]
    #     self.arm._total_car_count = 2 # 2 vehicles
    #     self.arm._total_wait_times = 3 # 3 seconds
    #     self.arm._max_wait_time = 2 # 2 seconds
    #     self.arm._max_queue_length = 5 # 5 vehicles
        
    #     # call move_all_vehicles
    #     self.arm.move_all_vehicles(7000, True, None, 1000, 1)

    #     # assert that the kpi values have been updated as intended
    #     self.assertEqual(self.arm._total_car_count, 4)
    #     self.assertEqual(self.arm._total_wait_times, 12)
    #     self.assertEqual(self.arm._max_wait_time, 6)
    #     self.assertEqual(self.arm._max_queue_length, 6)

    
    def test_handle_lane_switching(self):
        """Test that lane switching logic is correctly executed."""
        lane1 = MagicMock(spec=Lane)
        lane2 = MagicMock(spec=Lane)
        
        vehicle = MagicMock(spec=Vehicle)
        vehicle.destination = 1
        
        lane1.vehicles = [vehicle]
        lane2.vehicles = []
        lane2.allowed_directions = set([1, 2])
        
        # mock but should correlate to number of vehicles in the queue
        lane1.queue_length = 5
        lane2.queue_length = 3
        
        self.arm._lanes = [lane1, lane2]

        self.arm.move_vehicle_to_lane = MagicMock(return_value=True)
        self.arm.handle_lane_switching()
        self.arm.move_vehicle_to_lane.assert_called_once_with(vehicle, lane1, lane2)

    
    def test_move_vehicle_to_lane_success(self):
        """Test that a vehicle successfully moves to a new lane when there is space."""
        vehicle = MagicMock(spec=Vehicle)
        current_lane = MagicMock(spec=Lane)
        current_lane._queue_length = 4
        target_lane = MagicMock(spec=Lane)
        self.arm.enough_space_to_merge = MagicMock(return_value=1)
        
        result = self.arm.move_vehicle_to_lane(vehicle, current_lane, target_lane)
        target_lane.add_vehicle_to_index.assert_called_once_with(vehicle, 1)
        self.assertTrue(result)
        self.assertEqual(current_lane._queue_length, 3)
    
    def test_move_vehicle_to_lane_fail(self):
        """Test that a vehicle does not move to a new lane when there isn't enough space."""
        vehicle = MagicMock(spec=Vehicle)
        current_lane = MagicMock(spec=Lane)
        target_lane = MagicMock(spec=Lane)
        self.arm.enough_space_to_merge = MagicMock(return_value=-1)
        
        result = self.arm.move_vehicle_to_lane(vehicle, current_lane, target_lane)
        target_lane.add_vehicle_to_index.assert_not_called()
        self.assertFalse(result)
    
    def test_is_new_lane_shorter(self):
        """Test that lane comparison logic is correct."""
        lane1 = MagicMock(spec=Lane)
        lane2 = MagicMock(spec=Lane)
        lane1.queue_length = 5
        lane2.queue_length = 3
        self.assertTrue(self.arm.is_new_lane_shorter(lane1, lane2))
        self.assertFalse(self.arm.is_new_lane_shorter(lane2, lane1))

        

