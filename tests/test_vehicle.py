from unittest.mock import MagicMock
from Arm import Arm
from Lane import Lane, CarLane
from Vehicle import Vehicle, Car, Bus
from Box import Box
import unittest

class TestVehicle(unittest.TestCase):
    def setUp(self):
        self.vehicle = Car(18, 0, 1, 100)

    def test_movement(self):
        #Test movement for various intervals
        self.assertEqual(self.vehicle.get_next_position(10), 99.82)
        self.assertEqual(self.vehicle.get_next_position(100), 98.2)
        self.assertEqual(self.vehicle.get_next_position(1000), 82)
        self.assertEqual(self.vehicle.get_next_position(10000), -80)
    
    def test_relative_direction(self):
        #Test relative direction calculations
        vehicle1 = Car(18, 2, 3, 100) #Turning left
        vehicle2 = Car(18, 2, 1, 100) #Turning right
        vehicle3 = Car(18, 2, 0, 100) #Forwards
        vehicle4 = Car(18, 2, 2, 100) #U-Turn
        vehicle5 = Car(18, 1, 2, 100) #Turning left
        vehicle6 = Car(18, 1, 0, 100) #Turning right
        vehicle7 = Car(18, 1, 3, 100) #Forwards
        vehicle8 = Car(18, 1, 1, 100) #U-Turn
        #Left turns are 3 arms anticlockwise
        self.assertEqual(vehicle1.get_relative_direction(4), 3)
        self.assertEqual(vehicle5.get_relative_direction(4), 3)
        #Right turns are 1 arm anticlockwise
        self.assertEqual(vehicle2.get_relative_direction(4), 1)
        self.assertEqual(vehicle6.get_relative_direction(4), 1)
        self.assertEqual(vehicle3.get_relative_direction(4), 2)
        self.assertEqual(vehicle7.get_relative_direction(4), 2)
        self.assertEqual(vehicle4.get_relative_direction(4), 0)
        self.assertEqual(vehicle8.get_relative_direction(4), 0)

    
