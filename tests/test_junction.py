from unittest.mock import MagicMock
from Junction import Junction
import unittest
import numpy as np
from Vehicle import Car
from Arm import Arm
from Lane import Lane

class TestJunction(unittest.TestCase):
    def setUp(self):
        """ create a Junction before each test"""
        traffic_data = np.zeros((4, 4)).tolist()
        self.junction = Junction(traffic_data, num_lanes = 3)

    def test_get_kpi(self):
        """ integration test to see if junction can properly return kpi values"""
        # mock kpi values for each arm of the junction
        mock_kpi_values = [
            [10.5, 2.5, 5.9, 3],
            [15.2, 3.8, 6.3, 4],
            [12.0, 3.0, 5.4, 2],
            [20.1, 4.5, 7.8, 5] 
        ]
        
        # update each arm so it returns the mock kpi values when called
        for i, arm in enumerate(self.junction.arms):
            arm.get_kpi = MagicMock(return_value=mock_kpi_values[i])
        
        # assert that the get_kpi method returns the kpi values of each arm
        self.assertEqual(self.junction.get_kpi(), mock_kpi_values)

    def test_allowed_directions_none(self):
        """ test that if no allowed directions are given, all cars are allowed in all lanes"""
        for arm in self.junction.arms:
            for lane in arm._lanes:
                self.assertSetEqual(lane._allowed_directions, {0,1,2,3})

    def test_allowed_directions(self):
        """ test that when allowed directions are given, cars are restricted appropriately """
        #Initialise a junction with restricted directions
        junction1 = Junction(np.zeros((4, 4)).tolist(), allowed_lane_directions=[{1,2}, {3}, {1,3}], num_lanes = 3)
        #Destinations for left, forward and right cars from arm 2
        dests = [3, 0, 1]
        #Initialise list of cars
        cars = []
        #Create and try to add cars going in each direction
        for lane in range(3):
            for dest in range(3):
                cars.append(junction1.arms[2]._lanes[lane].create_vehicle(0, 2, dests[dest], "Car", 0))
        #Lane 0 should have left and forward vehicles
        self.assertIn(cars[0], junction1.arms[2]._lanes[0]._vehicles)
        self.assertIn(cars[1], junction1.arms[2]._lanes[0]._vehicles)
        self.assertNotIn(cars[2], junction1.arms[2]._lanes[0]._vehicles)
        #Lane 1 should have right vehicle
        self.assertNotIn(cars[3], junction1.arms[2]._lanes[1]._vehicles)
        self.assertNotIn(cars[4], junction1.arms[2]._lanes[1]._vehicles)
        self.assertIn(cars[5], junction1.arms[2]._lanes[1]._vehicles)
        #Lane 2 should have left and right vehicles
        self.assertIn(cars[6], junction1.arms[2]._lanes[2]._vehicles)
        self.assertNotIn(cars[7], junction1.arms[2]._lanes[2]._vehicles)
        self.assertIn(cars[8], junction1.arms[2]._lanes[2]._vehicles)