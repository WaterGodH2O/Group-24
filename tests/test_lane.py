from unittest.mock import MagicMock
from Lane import CarLane
import unittest


class TestLanes(unittest.TestCase):
    def setUp(self):
        """ create a CarLane before each test"""
        self.lane = CarLane([0, 1], 5, 100)
    
    def test_add_vehicle(self):
        """ should return true when added successfully """
        car = MagicMock()
        self.lane.add_vehicle(car)

        self.assertTrue(car in self.lane.vehicles)
    
    def test_remove_vehicle(self):
        """ should return the Vehicle we are removing from the lane"""
        # add a car to the lane
        car = MagicMock()
        self.lane.add_vehicle(car)

        # assert true if the vehicle no longer is in the line
        self.assertEqual(self.lane.remove_vehicle(car), car)
        self.assertTrue(car not in self.lane.vehicles)

    def test_remove_vehicle_not_in_lane(self):
        """ should return None """
        car = MagicMock()
        self.assertIsNone(self.lane.remove_vehicle(car))
        

    def test_last_vehicle(self):
        """ should return the last vehicle added to the lane """
        # create mock vehicles
        car1 = MagicMock()
        car2 = MagicMock()

        # add both mock cars to the lane
        self.lane.add_vehicle(car1)
        self.lane.add_vehicle(car2)

        self.assertEqual(self.lane.get_last_vehicle(), car2)
    
    def test_last_vehicle_empty(self):
        """ should return None when the lane is empty """
        self.assertIsNone(self.lane.get_last_vehicle())
    
    def test_vehicle_ahead(self):
        """ should return the vehicle in front of a given vehicle, or None when not found """
        # create mock vehicles
        car1 = MagicMock()
        car2 = MagicMock()

        # add both mock cars to the lane
        self.lane.add_vehicle(car1)
        self.lane.add_vehicle(car2)

        # test car 1 is ahead of car 2
        self.assertEqual(self.lane.get_vehicle_ahead(car2), car1)

        # test there are no cars ahead of car 1
        self.assertIsNone(self.lane.get_vehicle_ahead(car1))
    
    def test_vehicle_ahead_not_in_lane(self):
        """ should return None when the vehicle is not in the lane """
        # create a mock car
        car1 = MagicMock()
        self.assertIsNone(self.lane.get_vehicle_ahead(car1))

        # add a car to the lane to ensure result isn't affected
        car2 = MagicMock()
        self.lane.add_vehicle(car2)

        # test that it identifies car 1 still isn't in the lane
        self.assertIsNone(self.lane.get_vehicle_ahead(car1))
    
