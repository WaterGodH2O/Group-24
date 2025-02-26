from unittest.mock import MagicMock
from TrafficLight import TrafficLight
from Junction import Junction
from Vehicle import Car
import unittest
import numpy as np

class TestTrafficLight(unittest.TestCase):
    def setUp(self):
        """ create a junction before each test """
        self.junction = Junction(np.zeros((4,4)).tolist(), num_lanes = 3)

    def test_traffic_cycle_normal(self):
        """Test that when cars are present, traffic lights cycle as normal"""
        for i in range(4):
            #Add a car to each arm of the junction
            self.junction.arms[i]._lanes[1]._vehicles.append(Car(0, i, 0, 50, 4))
        #Test traffic light directions at various points in the simulation
        #Start at 0
        self.assertEqual(self.junction.traffic_light._traffic_light_dir, 0)
        #After 19.90s, still 0
        self.junction.simulate(19990, 10)
        self.assertEqual(self.junction.traffic_light._traffic_light_dir, 0)
        #After exactly 20s, change to -1 as all directions are red
        self.junction.simulate(10, 10)
        self.assertEqual(self.junction.traffic_light._traffic_light_dir, -1)
        self.junction.simulate(4990, 10)
        self.assertEqual(self.junction.traffic_light._traffic_light_dir, -1)
        #After 5s, change to 1
        self.junction.simulate(10, 10)
        self.assertEqual(self.junction.traffic_light._traffic_light_dir, 1)
        #After 24.90s, check in traffic light gap
        self.junction.simulate(24990, 10)
        self.assertEqual(self.junction.traffic_light._traffic_light_dir, -1)
        #After 25s, change to 2
        self.junction.simulate(10, 10)
        self.assertEqual(self.junction.traffic_light._traffic_light_dir, 2)
        #After 25s, change to 3
        self.junction.simulate(25000, 10)
        self.assertEqual(self.junction.traffic_light._traffic_light_dir, 3)
        #After 25s, change back to 0
        self.junction.simulate(25000, 10)
        self.assertEqual(self.junction.traffic_light._traffic_light_dir, 0)
        #Check a full light cycle occurs after 100s
        self.junction.simulate(100000, 10)
        self.assertEqual(self.junction.traffic_light._traffic_light_dir, 0)
    
    def test_traffic_light_cycle_single_skip(self):
        """Test that when a lane is empty, its lane is skipped"""
        for i in range(3):
            #Add a car to each arm of the junction except 3
            self.junction.arms[i]._lanes[1]._vehicles.append(Car(0, i, 0, 50, 4))
        #Check traffic light reaches direction 2 as normal
        self.junction.simulate(50000, 10)
        self.assertEqual(self.junction.traffic_light._traffic_light_dir, 2)
        #Check arm 3 is skipped
        self.junction.simulate(25000, 10)
        self.assertEqual(self.junction.traffic_light._traffic_light_dir, 0)

    def test_traffic_light_cycle_double_adj_skip(self):
        """When 2 lanes are empty, both are skipped"""
        for i in range(2):
            #Add a car to arms 0 and 1
            self.junction.arms[i]._lanes[1]._vehicles.append(Car(0, i, 0, 50, 4))
        #Check traffic light reaches direction 1 as normal
        self.junction.simulate(25000, 10)
        self.assertEqual(self.junction.traffic_light._traffic_light_dir, 1)
        #Check arms 2 and 3 are skipped
        self.junction.simulate(25000, 10)
        self.assertEqual(self.junction.traffic_light._traffic_light_dir, 0)
    
    def test_traffic_light_cycle_double_non_adj_skip(self):
        """When 2 non adjacent lanes are empty, the empty lane does not affect the cycle"""
        for i in range(2):
            #Add a car to arms 0 and 2
            self.junction.arms[2*i]._lanes[1]._vehicles.append(Car(0, 2*i, 0, 50, 4))
        self.assertEqual(self.junction.traffic_light._traffic_light_dir, 0)
        #Check arm 1 is skipped
        self.junction.simulate(25000, 10)
        self.assertEqual(self.junction.traffic_light._traffic_light_dir, 2)
        #Check arm 3 is skipped
        self.junction.simulate(25000, 10)
        self.assertEqual(self.junction.traffic_light._traffic_light_dir, 0)

    def test_traffic_light_cycle_triple_skip(self):
        """When all other lanes are empty, all other directions and the gap are skipped"""

        #Add a car to arm 0
        self.junction.arms[0]._lanes[1]._vehicles.append(Car(0, 0, 0, 50, 4))
        self.assertEqual(self.junction.traffic_light._traffic_light_dir, 0)
        #Check the light timer resets without setting all directions to red
        self.junction.simulate(20000, 10)
        self.assertEqual(self.junction.traffic_light._traffic_light_dir, 0)
    
    def test_traffic_light_cycle_empty(self):
        """When all lanes are empty, no cycling occurs"""
        for i in range(100):
            #Simulate 2 seconds 100 times
            self.junction.simulate(2000, 100)
            self.assertEqual(self.junction.traffic_light._traffic_light_dir, 0)

    