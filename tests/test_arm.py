from unittest.mock import MagicMock
from Arm import Arm
from Lane import Lane, CarLane, BusLane, LeftTurnLane
from Vehicle import Vehicle, Car, Bus
from Box import Box
import unittest

class TestArm(unittest.TestCase):
    def setUp(self):
        self.arm = Arm(2, 100, [20, 30, 40, 0], 3, 4, False, False, [{1}, {2}, {3}])

    def test_get_kpi(self):
        """ ensure that the correct kpi details are returned """
        # mock some kpi variables
        self.arm._total_wait_times = 30
        self.arm._total_car_count = 6
        self.arm._max_wait_time = 10
        self.arm._max_queue_length = 4

        # ensure that the get kpi method returns the correct values
        self.assertEqual(self.arm.get_kpi(), [5, 10, 4])

    def test_move_all_vehicles(self):
        # create some mock lanes
        lane1 = MagicMock(spec=Lane)
        lane2 = MagicMock(spec=Lane)
        lane3 = MagicMock(spec=Lane)

        # mock the queue length
        lane1.queue_length = 4
        lane2.queue_length = 2
        lane3.queue_length = 6

        # create mock cars for lanes 1 and 3 to return
        car1 = MagicMock(spec=Vehicle)
        car3 = MagicMock(spec=Vehicle)
        
        # mock the vehicle wait times
        car1.wait_time = 4000
        car3.wait_time = 1000

        # update the lane.move_all_vehicles return value for each lane to car1, {} and car3 respectively
        lane1.move_all_vehicles.return_value = {car1}
        lane2.move_all_vehicles.return_value = set()
        lane3.move_all_vehicles.return_value = {car3}

        box = Box(2, 3)

        # configure the arm
        self.arm._lanes = [lane1, lane2, lane3]
        self.arm._total_car_count = 2 # 2 vehicles
        self.arm._total_wait_times = 3 # 3 seconds
        self.arm._max_wait_time = 2 # 2 seconds
        self.arm._max_queue_length = 5 # 5 vehicles
        
        # call move_all_vehicles
        self.arm.move_all_vehicles(7000, True, box, 1000, 1)

        # assert that the kpi values have been updated as intended
        self.assertEqual(self.arm._total_car_count, 4)
        
        # assert that the wait times are correctly taken
        self.assertEqual(self.arm._total_wait_times, 8)

        # assert that the max wait time is properly updated
        self.assertEqual(self.arm._max_wait_time, 4)

        # assert that the max queue length hsa been properly updated
        self.assertEqual(self.arm._max_queue_length, 6)

    
    def test_handle_lane_switching_true(self):
        """Test that lane switching logic is correctly executed"""
        # create two mock lanes
        lane1 = CarLane({1, 2}, 15, 3, 4)
        lane2 = CarLane({1, 2}, 15, 3, 4)
        
        # create two mock cars
        vehicle1 = Car(5, 0, 1, 5, 4)
        vehicle2 = Car(5, 0, 1, 15, 4)
        
        # configure lanes
        lane1._vehicles = [vehicle1, vehicle2]
        lane1._queue_length = 2
        lane2._vehicles = []
        lane2._queue_length = 0

        # configure arm
        self.arm._lanes = [lane1, lane2]

        # switch lanes
        self.arm.handle_lane_switching()


        # assert that the first vehicle has switched lanes properly
        self.assertTrue(vehicle1 not in lane1.vehicles)
        self.assertTrue(vehicle1 in lane2.vehicles)

        # assert that the second vehicle hasn't switched lanes
        self.assertTrue(vehicle2 in lane1.vehicles)


    def test_handle_lane_switching_false(self):
        """Test that vehicles don't switch lane with valid counts"""
        # TODO extend properly to check it doesn't switch lane if can't enter
        # create two mock lanes
        lane1 = CarLane({1}, 15, 3, 4)
        lane2 = CarLane({1, 2}, 15, 3, 4)
        
        # create two mock cars
        vehicle1 = Car(5, 0, 1, 5, 4)
        
        # configure lanes
        lane1._vehicles = [vehicle1]
        lane1._queue_length = 1
        lane2._vehicles = []
        lane2._queue_length = 0
        lane2._allowed_directions = {1, 2}

        # configure arm
        self.arm._lanes = [lane1, lane2]

        # switch lanes
        self.arm.handle_lane_switching()

        # assert that the first vehicle has switched lanes properly
        self.assertTrue(vehicle1 in lane1.vehicles)
        self.assertTrue(vehicle1 not in lane2.vehicles)
        
    
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
    
    def test_enough_space_to_merge_true(self):
        """ Tests vehicles can merge into lane on valid and boundary cases """
        # mock the vehicle we want to merge
        car1 = MagicMock(spec=Vehicle)
        car1.distance = 6
        car1._stopping_distance = 5
        
        # mock vehicles already in the lane
        car2 = MagicMock(spec=Vehicle)
        car3 = MagicMock(spec=Vehicle)
        car2.distance = 0
        car2._stopping_distance = 5
        car3.distance = 12
        car3._stopping_distance = 5

        # mock the lane to merge into
        lane = MagicMock(spec=Lane)
        lane.vehicles = [car2, car3]
        
        # assert that we can merge into the lane at index 1
        space_to_merge = self.arm.enough_space_to_merge(car1, lane)
        self.assertEqual(space_to_merge, 1)

        # test we can merge into index 0 if no car ahead
        lane.vehicles = [car3]
        space_to_merge = self.arm.enough_space_to_merge(car1, lane)
        self.assertEqual(space_to_merge, 0)

        # test we can merge into the lane if no cars behind
        lane.vehicles = [car2]
        space_to_merge = self.arm.enough_space_to_merge(car1, lane)
        self.assertEqual(space_to_merge, 1)

        # test we can merge into the lane if it is empty
        lane.vehicles = []
        space_to_merge = self.arm.enough_space_to_merge(car1, lane)
        self.assertEqual(space_to_merge, 0)

    def test_enough_space_to_merge_false(self):
        """ Tests vehicles can merge into lane on invalid cases """
        # mock the vehicle we want to merge
        car1 = MagicMock(spec=Vehicle)
        car1.distance = 6
        car1._stopping_distance = 5
        
        # mock vehicles already in the lane
        car2 = MagicMock(spec=Vehicle)
        car3 = MagicMock(spec=Vehicle)
        car2.distance = 3
        car2._stopping_distance = 5
        car3.distance = 12
        car3._stopping_distance = 5

        # mock the lane to merge into
        lane = MagicMock(spec=Lane)
        lane.vehicles = [car2, car3]
        
        # assert that we can't merge when vehicle ahead is too close
        space_to_merge = self.arm.enough_space_to_merge(car1, lane)
        self.assertEqual(space_to_merge, -1)

        # assert we can't merge when the vehicle behind is too closee
        car2.distance = 0
        car3.distance = 8
        space_to_merge = self.arm.enough_space_to_merge(car1, lane)
        self.assertEqual(space_to_merge, -1)

        # assert we can't merge when vehicle behind has same distance
        car3.distance = 6
        space_to_merge = self.arm.enough_space_to_merge(car1, lane)
        self.assertEqual(space_to_merge, -1)

        # assert we can't merge when vehicle ahead has same distance
        car2.distance = 6
        car3.distance = 12
        space_to_merge = self.arm.enough_space_to_merge(car1, lane)
        self.assertEqual(space_to_merge, -1)

        # assert we can't merge when any vehicle has a boundary distance
        car2.distance = 1
        space_to_merge = self.arm.enough_space_to_merge(car1, lane)
        self.assertEqual(space_to_merge, -1)

    
    def test_is_new_lane_shorter(self):
        """Test that lane comparison logic is correct."""
        lane1 = MagicMock(spec=Lane)
        lane2 = MagicMock(spec=Lane)
        lane1.queue_length = 5
        lane2.queue_length = 3
        self.assertTrue(self.arm.is_new_lane_shorter(lane1, lane2))
        self.assertFalse(self.arm.is_new_lane_shorter(lane2, lane1))

        
    def test_get_kpi(self):
        """ Tests that calculations are performed correctly to get KPI """
        self.arm._total_wait_times = 60
        self.arm._max_wait_time = 20
        self.arm._total_car_count = 8
        self.arm._max_queue_length = 4

        # configure mock cars
        car1 = MagicMock(spec=Vehicle)
        car1.wait_time = 25000
        car2 = MagicMock(spec=Vehicle)
        car2.wait_time = 15000

        # configure lanes
        lane1 = MagicMock(spec=Lane)
        lane2 = MagicMock(spec=Lane)
        self.arm._lanes = [lane1, lane2]
        lane1.vehicles = [car1]
        lane2.vehicles = [car2]
        
        # calculate the kpi metrics
        kpi_metrics = self.arm.get_kpi()

        
        # assert that the correct average wait time is returned
        # (60 + 15 + 25) / (8 + 2) = 10
        self.assertEqual(kpi_metrics[0], 10.0)

        # assert that the correct max wait time is returned
        self.assertEqual(kpi_metrics[1], 25.0)

        # assert that the correct max queue length is returned
        self.assertEqual(kpi_metrics[2], 4)

    def test_no_vehicles_within_true(self):
        """ Test the program can accurately determine if there are no vehicles within
        a distance from the junction """
        
        # create mock lanes
        lane1 = MagicMock(spec=Lane)
        lane2 = MagicMock(spec=Lane)

        # create mock vehicles
        car1 = MagicMock(spec=Vehicle)
        car1.distance = 150
        car2 = MagicMock(spec=Vehicle)
        car2.distance = 75

        self.arm._lanes = [lane1, lane2]
        
        # asserts true when there are no vehicles in the lanes
        lane1.get_first_vehicle.return_value = None
        lane2.get_first_vehicle.return_value = None
        self.assertTrue(self.arm.no_vehicles_within(100))

        # asserts false when there is a vehicle within 100m of a junction
        lane1.get_first_vehicle.return_value = car1
        lane2.get_first_vehicle.return_value = car2
        self.assertFalse(self.arm.no_vehicles_within(100))

        # assert true when none of the vehicles are within 100m of the junction
        car2.distance = 175
        self.assertTrue(self.arm.no_vehicles_within(100))

    def test_lane_creation(self):
        """ Tests that bus lanes, car lanes and left turn lanes are properly created """
        # test lane configurations are properly passed in
        self.arm._allowed_directions = [{1}, {1, 2}, {3}]
        self.arm.create_lanes(False, False, 50, 100, 3)

        # assert that the allowed directions for the lanes match
        for i, lane in enumerate(self.arm._lanes):
            self.assertEqual(lane.allowed_directions, self.arm._allowed_directions[i])
        
        
        # test bus lane is properly created
        self.arm._allowed_directions = [{1, 2}, {3}]
        self.arm.create_lanes(True, False, 50, 100, 3)
        lane = self.arm._lanes

        # check the first lane is a bus lane
        self.assertIsInstance(lane[0], BusLane)
        self.assertEqual(lane[0].allowed_directions, {1, 2, 3})

        #  check the remaining lanes are care lanes and properly allocated
        self.assertIsInstance(lane[1], CarLane)
        self.assertIsInstance(lane[2], CarLane)
        self.assertEqual(lane[1].allowed_directions, self.arm._allowed_directions[0])
        self.assertEqual(lane[2].allowed_directions, self.arm._allowed_directions[1])

        
        # test left turn lane is properly created
        self.arm._allowed_directions = [{1}, {1}, {2, 3}, {3}]
        self.arm.create_lanes(False, True, 50, 100, 4)
        lane = self.arm._lanes

        # check the first two lanes are left turn lanes (can only go left)
        self.assertIsInstance(lane[0], LeftTurnLane)
        self.assertIsInstance(lane[1], LeftTurnLane)
        self.assertEqual(lane[0].allowed_directions, {1})
        self.assertEqual(lane[1].allowed_directions, {1})

        #  check the remaining lanes are care lanes and properly allocated
        self.assertIsInstance(lane[2], CarLane)
        self.assertIsInstance(lane[3], CarLane)
        self.assertEqual(lane[2].allowed_directions, self.arm._allowed_directions[2])
        self.assertEqual(lane[3].allowed_directions, self.arm._allowed_directions[3])

    def test_collisions_forward(self):
        """Test that when a car is moving forward in the middle lane, vehicles turning across the junction can't"""
        blocking_car = Car(10, 2, 0, 20, 4)
        blocking_car._source_lane = 1
        box = Box(3, 4)
        box.add_vehicle(blocking_car)
        #Create 3 cars to test in each lane (left, forward, right)
        cars = [Car(10, 2, 3, 0, 4), Car(10, 2, 0, 0, 4), Car(10, 2, 1, 0, 4)]

        for lane in range(3):
            for car in range(3):
                #Reset car distance between tests
                cars[car]._distance = 0
                #Add car to lane
                self.arm._lanes[lane]._vehicles.append(cars[car])
                #Move vehicles
                self.arm.move_all_vehicles(0, 2, box, 100, 2)
                if (lane, car) == (0, 2) or (lane, car) == (2, 0):
                    #If in the left lane turning right or right lane turning left, it should be blocked
                    self.assertNotIn(cars[car], box._vehicles)
                    self.arm._lanes[lane].remove_vehicle(cars[car])
                else:
                    #Otherwise, it should not be blocked
                    self.assertIn(cars[car], box._vehicles)
                    box._vehicles.remove(cars[car])
    
    def test_collisions_left(self):
        """Test that when a car is turning left in the middle lane, it blocks all vehicles in the left lane not also turning left"""
        blocking_car = Car(10, 2, 3, 20, 4)
        blocking_car._source_lane = 1
        box = Box(3, 4)
        box.add_vehicle(blocking_car)
        #Create 3 cars to test in each lane (left, forward, right)
        cars = [Car(10, 2, 3, 0, 4), Car(10, 2, 0, 0, 4), Car(10, 2, 1, 0, 4)]

        for lane in range(3):
            for car in range(3):
                #Reset car distance between tests
                cars[car]._distance = 0
                #Add car to lane
                self.arm._lanes[lane]._vehicles.append(cars[car])
                #Move vehicles
                self.arm.move_all_vehicles(0, 2, box, 100, 2)
                if (lane, car) == (0, 1) or (lane, car) == (0, 2):
                    #If in the left lane and not turning left, it should be blocked
                    self.assertNotIn(cars[car], box._vehicles)
                    self.arm._lanes[lane].remove_vehicle(cars[car])
                else:
                    #Otherwise, it should not be blocked
                    self.assertIn(cars[car], box._vehicles)
                    box._vehicles.remove(cars[car])

    def test_collisions_right(self):
        """Test that when a car is turning right in the middle lane, it blocks all vehicles in the right lane not also turning right"""
        blocking_car = Car(10, 2, 1, 20, 4)
        blocking_car._source_lane = 1
        box = Box(3, 4)
        box.add_vehicle(blocking_car)
        #Create 3 cars to test in each lane (left, forward, right)
        cars = [Car(10, 2, 3, 0, 4), Car(10, 2, 0, 0, 4), Car(10, 2, 1, 0, 4)]

        for lane in range(3):
            for car in range(3):
                #Reset car distance between tests
                cars[car]._distance = 0
                #Add car to lane
                self.arm._lanes[lane]._vehicles.append(cars[car])
                #Move vehicles
                self.arm.move_all_vehicles(0, 2, box, 100, 2)
                if (lane, car) == (2, 1) or (lane, car) == (2, 0):
                    #If in the left lane and not turning left, it should be blocked
                    self.assertNotIn(cars[car], box._vehicles)
                    self.arm._lanes[lane].remove_vehicle(cars[car])
                else:
                    #Otherwise, it should not be blocked
                    self.assertIn(cars[car], box._vehicles)
                    box._vehicles.remove(cars[car])

class TestBusLeftTurnArm(unittest.TestCase):
    #Tests for arms that have bus lanes and left turn lanes
    def setUp(self):
        lane_config = [{1}, {2, 3}]
        self.arm = Arm(3, 1000, [0,0,0,0], 3, 4, True, True, lane_config)
    
    def test_vehicle_creation(self):
        """Test that buses add to lane 0, left turning cars to lane 1, others to lane 2"""
        #Add vehicles
        self.arm.create_vehicle(10, 2, 3, "Bus")
        self.arm.create_vehicle(10, 2, 3, "Car")
        self.arm.create_vehicle(10, 2, 1, "Car")
        #Check bus in lane 0
        self.assertEqual(self.arm._lanes[0]._vehicles[0].vehicle_type, "Bus")
        #Check left turning car in lane 1
        self.assertEqual(self.arm._lanes[1]._vehicles[0].vehicle_type, "Car")
        self.assertEqual(self.arm._lanes[1]._vehicles[0].get_relative_direction(), 3)
        #Check right turning car in lane 2
        self.assertEqual(self.arm._lanes[2]._vehicles[0].vehicle_type, "Car")
        self.assertNotEqual(self.arm._lanes[2]._vehicles[0].get_relative_direction(), 3)

    def test_bus_lane_switching_success(self):
        """Test that buses can move into bus lanes"""
        #Create cars and a bus
        car1 = Car(10, 2, 3, 0, 4)
        car2 = Car(10, 2, 3, 8, 4)
        bus = Bus(10, 2, 3, 16, 4)
        for v in [car1, car2, bus]:
            self.arm._lanes[1].add_vehicle(v)

        self.arm.handle_lane_switching()

        self.assertIn(bus, self.arm._lanes[0]._vehicles)
    
    def test_bus_lane_switching_fail(self):
        """Test that cars can't move into bus lanes"""
        #Create cars and a bus
        car1 = Car(10, 2, 3, 0, 4)
        car2 = Car(10, 2, 3, 8, 4)
        car3 = Car(10, 2, 3, 16, 4)
        for v in [car1, car2, car3]:
            self.arm._lanes[1].add_vehicle(v)

        self.arm.handle_lane_switching()
        #Check the bus lane is empty
        self.assertFalse(self.arm._lanes[0]._vehicles)

    def test_left_turn_lane_switch_success(self):
        """ Test left turning vehicles can move into the left turn lane """
        #Initialise buses
        bus1 = Bus(10, 2, 3, 0, 4)
        bus2 = Bus(10, 2, 3, 15, 4)
        for bus in [bus1, bus2]:
            self.arm._lanes[0].add_vehicle(bus)
        car2 = Car(10, 2, 3, 100, 4)
        car1 = Car(10, 2, 1, 90, 4)
        for c in [Car(10, 2, 1, i, 4) for i in range(0, 90, 10)] + [car1] + [car2]:
            self.arm._lanes[2].add_vehicle(c)

        self.arm.handle_lane_switching()

        #Check that the cars and buses turning left move to lane 1
        self.assertIn(bus2, self.arm._lanes[1]._vehicles)
        self.assertIn(car2, self.arm._lanes[1]._vehicles)

    def test_left_turn_lane_switch_fail(self):
        """ Test right turning vehicles can't move into the left turn lane """
        #Initialise buses
        bus1 = Bus(10, 2, 3, 0, 4)
        bus2 = Bus(10, 2, 1, 15, 4)
        for bus in [bus1, bus2]:
            self.arm._lanes[0].add_vehicle(bus)
        car2 = Car(10, 2, 1, 100, 4)
        car1 = Car(10, 2, 1, 90, 4)
        for c in [Car(10, 2, 1, i, 4) for i in range(0, 90, 10)] + [car1] + [car2]:
            self.arm._lanes[2].add_vehicle(c)

        self.arm.handle_lane_switching()

        #Check that cars and buses that otherwise could move into the lane are prevented by their turning direction
        self.assertNotIn(bus2, self.arm._lanes[1]._vehicles)
        self.assertNotIn(car2, self.arm._lanes[1]._vehicles)

    def test_ltl_traffic_light_success(self):
        """ Test that vehicles move into the box when either"""
    def test_vehicle_collision_ltl_success(self):
        """ Test that vehicles in a left turn lane can enter when there are vehicles moving in the same direction or going to different arms """
        #Initalise vehicles
        #Target vehicle
        car1 = Car(10, 2, 3, 0, 4)
        #Vehicles that should not block car1
        car2 = Car(10, 2, 3, 5, 4)
        car3 = Car(10, 1, 2, 5, 4)
        box = Box(3, 3)
        #Add cars 2 and 3 to box, car 1 to lt lane
        box._vehicles.append(car2)
        box._vehicles.append(car3)
        self.arm._lanes[1]._vehicles.append(car1)

        self.arm.move_all_vehicles(0, 1, box, 100, 2)

        self.assertIn(car1, box._vehicles)

    def test_vehicle_collision_ltl_fail(self):
        """ Test that vehicles in a left turn lane can't enter when other vehicles in the box are moving to the same arm """
        #Initalise vehicles
        #Target vehicle
        car1 = Car(10, 2, 3, 0, 4)
        #This comes from a different arm and goes to the same arm, so has priority.
        car2 = Car(10, 1, 3, 5, 4)
        box = Box(3, 3)
        #Add car 2 to box, car 1 to lt lane
        box._vehicles.append(car2)
        self.arm._lanes[1]._vehicles.append(car1)

        self.arm.move_all_vehicles(0, 1, box, 100, 2)

        self.assertNotIn(car1, box._vehicles)

    def test_normal_collisions_ltl(self):
        """Test that when a car is moving in a left turn lane it does not block anything"""
        blocking_car = Car(10, 0, 1, 20, 4)
        blocking_car._source_lane = 1
        box = Box(3, 4)
        box.add_vehicle(blocking_car)
        #Create 3 cars to test in each lane (left, forward, right)
        cars = [Car(10, 2, 3, 0, 4), Car(10, 2, 0, 0, 4), Car(10, 2, 1, 0, 4)]

        for lane in range(3):
            for car in range(3):
                #Reset car distance between tests
                cars[car]._distance = 0
                #Add car to lane
                self.arm._lanes[lane]._vehicles.append(cars[car])
                #Move vehicles
                self.arm.move_all_vehicles(0, 2, box, 100, 2)
                #Nothing should be blocked
                self.assertIn(cars[car], box._vehicles)
                box._vehicles.remove(cars[car])