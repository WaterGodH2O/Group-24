from unittest.mock import MagicMock
from Junction import Junction
import unittest
import numpy as np

class TestJunction(unittest.TestCase):
    def setUp(self):
        """ create a Junction before each test"""
        traffic_data = np.zeros((4, 4)).tolist()
        self.junction = Junction(traffic_data)

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
