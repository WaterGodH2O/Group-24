from unittest.mock import MagicMock
from Arm import Arm
from Lane import Lane, CarLane
from Vehicle import Vehicle, Car
from Box import Box
import unittest

class TestBox(unittest.TestCase):
    def setUp(self):
        self.box = Box(3, 3)
    
    def test_vehicle_addition(self):
        #Initialise vehicles
        vehicle1 = Car(18, 0, 0, 2, 4)
        vehicle2 = Car(18, 0, 0, 0, 4)
        vehicle3 = Car(18, 0, 0, -2, 4)
        #Add to box
        self.box.add_vehicle(vehicle1)
        self.box.add_vehicle(vehicle2)
        self.box.add_vehicle(vehicle3)
        #Check all vehicles have been added to the box at the right distance
        self.assertEqual(vehicle1.distance, 20)
        self.assertEqual(vehicle2.distance, 18)
        self.assertEqual(vehicle3.distance, 16)
        self.assertIn(vehicle1, self.box._vehicles)
        self.assertIn(vehicle2, self.box._vehicles)
        self.assertIn(vehicle3, self.box._vehicles)
    
    def test_vehicle_exit(self):
        #Initialise vehicles to 2m, 1m, 0m and -2m from the end of the box
        vehicle0 = Car(20, 0, 0, -16, 4)
        vehicle1 = Car(20, 0, 0, -17, 4)
        vehicle2 = Car(20, 0, 0, -18, 4)
        vehicle3 = Car(20, 0, 0, -20, 4)
        #Add to box
        self.box.add_vehicle(vehicle0)
        self.box.add_vehicle(vehicle1)
        self.box.add_vehicle(vehicle2)
        self.box.add_vehicle(vehicle3)
        #Move all vehicles
        self.box.move_all_vehicles(50)
        #Check vehicle 0 hasn't left and all others have.
        self.assertIn(vehicle0, self.box._vehicles)
        self.assertNotIn(vehicle1, self.box._vehicles)
        self.assertNotIn(vehicle2, self.box._vehicles)
        self.assertNotIn(vehicle3, self.box._vehicles)
        self.assertEqual(vehicle0.distance, 1)
        #Move again, and check vehicle 0 has left
        self.box.move_all_vehicles(50)
        self.assertNotIn(vehicle0, self.box._vehicles)

