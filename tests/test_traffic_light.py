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
            #Simulate random amounts of time
            self.junction.simulate(self.junction.random.uniform(10, 1000), 10)
            self.assertEqual(self.junction.traffic_light._traffic_light_dir, -1)

class TestPedestrianCrossing(unittest.TestCase):
    def setUp(self):
        """Create a junction with a pedrestrian crossing"""
        self.junction = Junction(np.zeros((4,4)).tolist(),
                                 num_lanes = 3,
                                 pedestrian_crossing = True,
                                 p_crossing_freq = 1,
                                 p_crossing_time_s = 10)
        #Store traffic light as t
        self.t = self.junction.traffic_light
        #Create constant DAY, which is 1 day in ms
        self.DAY = 86400000
        #Set the time until next crossing to 1 day, to avoid randomness
        self.t.p_crossing_interval_time_ms = self.DAY
        
    def test_cycle_cars_present_all_lanes(self):
        """Test that pedestrian crossing requests are queued and activated correctly when cars are present"""
        for i in range(4):
            #Add a car to each arm of the junction
            self.junction.arms[i]._lanes[1]._vehicles.append(Car(0, i, 0, 50, 4))
        
        #Run a test to check 1 full cycle with crossing requests throughout
        self.normal_cycle_test()
        

        #Check request still exits and normal traffic has resumed
        self.assertTrue(self.t.p_crossing_queued)
        self.assertEqual(self.t._traffic_light_dir, 1)
        self.assertEqual(self.t.traffic_light_time_ms, 20000)
        #Check that after another full cycle the crossing is not queued
        self.junction.simulate(35000, 100)
        self.assertFalse(self.t.p_crossing_queued)
        self.assertEqual(self.t._traffic_light_dir, 2)
        self.assertEqual(self.t.traffic_light_time_ms, 20000)
        #Check that a cycle without a crossing is 25s long
        self.junction.simulate(25000, 100)
        self.assertFalse(self.t.p_crossing_queued)
        self.assertEqual(self.t._traffic_light_dir, 3)
        self.assertEqual(self.t.traffic_light_time_ms, 20000)

    def test_cycle_2_cars_missing(self):
        """ Test that 2 arms not having cars does not affect the cycle """
        for i in range(2):
            #Add cars to arms 0 and 2
            self.junction.arms[2*i]._lanes[1]._vehicles.append(Car(0, 2*i, 0, 50, 4))
        
        #Run a test to check 1 full cycle with crossing requests throughout
        self.normal_cycle_test()
        

        #Perform the same checks as in the all_cars test, but with different traffic light directions
        self.assertTrue(self.t.p_crossing_queued)
        self.assertEqual(self.t._traffic_light_dir, 2)
        self.assertEqual(self.t.traffic_light_time_ms, 20000)
        self.junction.simulate(35000, 100)
        self.assertFalse(self.t.p_crossing_queued)
        self.assertEqual(self.t._traffic_light_dir, 0)
        self.assertEqual(self.t.traffic_light_time_ms, 20000)
        self.junction.simulate(25000, 100)
        self.assertFalse(self.t.p_crossing_queued)
        self.assertEqual(self.t._traffic_light_dir, 2)
        self.assertEqual(self.t.traffic_light_time_ms, 20000)

    def test_cycle_3_cars_missing(self):
        """ Test that 3 arms not having cars (and therefore no normal green light changes) does not affect the cycle """
        self.junction.arms[0]._lanes[1]._vehicles.append(Car(0, 0, 0, 50, 4))
        
        #Run a test to check 1 full cycle with crossing requests throughout
        self.normal_cycle_test()
        

        #Perform the same checks as in the all_cars test, but with different traffic light directions
        self.assertTrue(self.t.p_crossing_queued)
        self.assertEqual(self.t._traffic_light_dir, 0)
        self.assertEqual(self.t.traffic_light_time_ms, 20000)
        self.junction.simulate(35000, 100)
        self.assertFalse(self.t.p_crossing_queued)
        self.assertEqual(self.t._traffic_light_dir, 0)
        self.assertEqual(self.t.traffic_light_time_ms, 20000)
        #When lights don't change, there is no 5s gap so the direction will reset 5s earlier than normal
        self.junction.simulate(20000, 100)
        self.assertFalse(self.t.p_crossing_queued)
        self.assertEqual(self.t._traffic_light_dir, 0)
        self.assertEqual(self.t.traffic_light_time_ms, 20000)

    def test_empty_junction(self):
        """ Test that when the junction is empty it immediately starts a crossing """
        #Set crossing interval to 0
        self.t.p_crossing_interval_time_ms = 0
        #Simulate 1 ms
        self.junction.simulate(1, 1)
        #Set crossing interval back to 1 day and check a crossing is queued
        self.t.p_crossing_interval_time_ms = self.DAY
        self.assertTrue(self.t.p_crossing_queued)
        #Simulate 1 ms
        self.junction.simulate(1, 1)
        #Check the crossing activated
        self.assertEqual(self.t.p_crossing_timer_ms, 10000)
        #Simulate 15s
        self.junction.simulate(15000, 100)
        #Check that the pedestrian crossing has ended, but the gap is still at 5000ms as it is constantly refreshed when the junction is empty
        self.assertFalse(self.t.p_crossing_queued)
        self.assertEqual(self.t._traffic_light_dir, -1)
        self.assertLessEqual(self.t.p_crossing_timer_ms, 0)
        self.assertEqual(self.t.traffic_light_gap_timer_ms, 5000)

    def test_start_empty_junction(self):
        """ Test that crossings act normally when a car is created midway through """
        #Set crossing interval to 0
        self.t.p_crossing_interval_time_ms = 0
        #Simulate 1 ms
        self.junction.simulate(1, 1)
        #Set crossing interval back to 1 day and check a crossing is queued
        self.t.p_crossing_interval_time_ms = self.DAY
        self.assertTrue(self.t.p_crossing_queued)
        #Simulate 1 ms
        self.junction.simulate(1, 1)
        #Check the crossing activated
        self.assertEqual(self.t.p_crossing_timer_ms, 10000)
        #Simulate 7.5s
        self.junction.simulate(7500, 100)
        #Create a car
        self.junction.arms[0]._lanes[1]._vehicles.append(Car(0, 0, 2, 50, 4))
        #Check that 0.5s later the pedestrian crossing is still normal
        self.junction.simulate(500, 100)
        self.assertEqual(self.t._traffic_light_dir, -1)
        self.assertEqual(self.t.p_crossing_timer_ms, 2000)
        self.junction.simulate(2000, 100)
        #Check that the pedestrian crossing has ended and the gap has started
        self.assertFalse(self.t.p_crossing_queued)
        self.assertEqual(self.t._traffic_light_dir, -1)
        self.assertLessEqual(self.t.p_crossing_timer_ms, 0)
        self.assertEqual(self.t.traffic_light_gap_timer_ms, 5000)
        #Check the gap ends as normal
        self.junction.simulate(5000, 100)
        self.assertEqual(self.t._traffic_light_dir, 0)


    def normal_cycle_test(self):
        """ Called by other tests to check pedestrian crossing requests are handled correctly"""
        #Wait 10 seconds
        self.junction.simulate(10000, 100)
        #Check no crossing is queued yet
        self.assertFalse(self.t.p_crossing_queued)

        #Create 9 crossing requests, checking each time that a crossing is queued but inactive
        for _ in range(9):
            #Set crossing interval to 0
            self.t.p_crossing_interval_time_ms = 0
            #Simulate 1 ms
            self.junction.simulate(1, 1)
            #Set crossing interval back to 1 day and check a crossing is queued but not activated
            self.t.p_crossing_interval_time_ms = self.DAY
            self.assertTrue(self.t.p_crossing_queued)
            self.assertNotEqual(self.t._traffic_light_dir, -1)

        #Simulate 9990 ms to get to 1ms before the light turns red
        self.junction.simulate(90, 10)
        self.junction.simulate(9900, 100)

        #Check request still exits and is inactive
        self.assertTrue(self.t.p_crossing_queued)
        self.assertNotEqual(self.t._traffic_light_dir, -1)
        #Simulate 1ms
        self.junction.simulate(1,1)
        #Check traffic in all directions is paused
        self.assertEqual(self.t._traffic_light_dir, -1)

        #Simulate 9.9 seconds for the crossing time
        self.junction.simulate(9900, 100)
        #Check the crossing is still queued
        self.assertTrue(self.t.p_crossing_queued)
        self.junction.simulate(100,100)
        #Check light is still off (5 seconds time between light changes still aplies)
        self.assertEqual(self.t._traffic_light_dir, -1)
        #Check crossing is unqueued
        self.assertFalse(self.t.p_crossing_queued)

        #Start another request as soon as possible
        self.t.p_crossing_interval_time_ms = 0
        #Simulate 1 ms
        self.junction.simulate(1, 1)
        #Set crossing interval back to 1 day and check a crossing is queued and not active
        self.t.p_crossing_interval_time_ms = self.DAY
        self.assertTrue(self.t.p_crossing_queued)
        self.assertLessEqual(self.t.p_crossing_timer_ms, 0)
        
        #Simulate 99ms, then 4900ms to get to the end of the gap
        self.junction.simulate(99, 1)
        self.junction.simulate(4900, 100)