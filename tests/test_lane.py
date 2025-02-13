from unittest.mock import MagicMock
from Lane import CarLane
from Vehicle import Vehicle
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

    def test_move_all_vehicles_red(self):
        """ tests if vehicles (not waiting in a queue) can still move even if the light is red """
        # create mock vehicles
        car1 = MagicMock(spec=Vehicle)
        car2 = MagicMock(spec=Vehicle)
        car3 = MagicMock(spec=Vehicle)
        car4 = MagicMock(spec=Vehicle)

        # set mock values
        car1._distance = 0
        car1._speed = 2
        car1._stopping_distance = 5

        car2._distance = 5
        car2._speed = 2
        car2._stopping_distance = 5

        car3._distance = 11
        car3._speed = 2
        car3._stopping_distance = 5

        car4._distance = 20
        car4._speed = 2
        car4._stopping_distance = 5

        # create lane with mock vehicles
        self.lane._vehicles = [car1, car2, car3, car4]

        # update the positions of all cars (per 1 second)
        leaving_vehicle = self.lane.move_all_vehicles(False, 1000)

        # assert that the right vehicles have moved (cars 3 and 4 should have move 2m in 1 second (2m/s))
        self.assertEqual(leaving_vehicle, None)
        self.assertEqual(car1._distance, 0)
        self.assertEqual(car2._distance, 5)
        self.assertEqual(car3._distance, 10)
        self.assertEqual(car4._distance, 18)

    
    def test_move_all_vehicles_green(self):
        """ test that the right vehicles move when the light is green """
        # create mock vehicles
        car1 = MagicMock(spec=Vehicle)
        car2 = MagicMock(spec=Vehicle)
        car3 = MagicMock(spec=Vehicle)
        car4 = MagicMock(spec=Vehicle)

        # set mock values
        car1._distance = 0
        car1._speed = 2
        car1._stopping_distance = 5

        car2._distance = 5
        car2._speed = 2
        car2._stopping_distance = 5

        car3._distance = 10
        car3._speed = 2
        car3._stopping_distance = 5

        car4._distance = 13
        car4._speed = 2
        car4._stopping_distance = 5

        # create lane with mock vehicles
        self.lane._vehicles = [car1, car2, car3, car4]

        # update the positions of all cars (per 1 second)
        leaving_vehicle = self.lane.move_all_vehicles(True, 1000)
        
        # assert that the right vehicles have moved (cars 3 and 4 should have move 2m in 1 second (2m/s))
        self.assertEqual(leaving_vehicle, car1) # assert that car 1 has left the junction
        self.assertEqual(car2._distance, 3)
        self.assertEqual(car3._distance, 8)
        self.assertEqual(car4._distance, 13)


    
