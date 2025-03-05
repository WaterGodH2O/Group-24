from typing import List, Set
from abc import ABC, abstractmethod
from Vehicle import Vehicle, Car, Bus
from Box import Box

class Lane(ABC):
    """
    The abstract class Lane, which defines the basic interface for all lanes.
    """
    def __init__(self, 
                 allowed_directions: Set[int], 
                 width: int, 
                 length: int,
                 num_arms: int):
        # the list of all vehicles currently in this lane
        self._vehicles: List[Vehicle] = []

        # the directions vehicles in this lane can go
        self._allowed_directions: Set[int] = allowed_directions

        # the width of the lane
        self._width: int = width
        self._length: int = length

        # the number of vehicles currently in the lane
        self.queue_length: int = 0

        # the number of arms in the junction
        self._num_arms: int = num_arms

    @property
    def allowed_directions(self) -> Set[int]:
        """ Returns the directions cars in this lane are allowed to travel """
        return self._allowed_directions
    @property
    def vehicles(self) -> List[Vehicle]:
        return self._vehicles
    @property
    def width(self) -> int:
        return self._width
    @property
    def length(self) -> int:
        return self._length

    def get_first_vehicle(self) -> Vehicle:
        """
        Method to get the first vehicle currently in this lane

        :return: The first vehicle in the lane or None if the list is empty
        """
        
        # return the first index of the list or none if empty
        return self._vehicles[0] if self._vehicles else None
    
    def get_last_vehicle(self) -> Vehicle:
        """
        Method to get the last vehicle currently in this lane

        :return: The last vehicle in the lane or None if the list is empty
        """
        
        # return the last index of the list or none if empty
        return self._vehicles[-1] if self._vehicles else None
    
    def get_vehicle_ahead(self, current_vehicle: Vehicle) -> Vehicle:
        """
        Method to get the vehicle in front of a given vehicle

        :param current_vehicle: The vehicle which we want to find the next vehicle from
        :return: The next vehicle in the lane or None if the list is empty
        """
        try:
            # try to find the index of the vehicle in front of the current vehicle
            vehicle_ahead_index = self._vehicles.index(current_vehicle) - 1
            
            # return None if there aren't any vehicles in front of the current vehicle
            if vehicle_ahead_index < 0:
                return None
            
            # return the vehicle in front of the current vehicle
            return self._vehicles[vehicle_ahead_index]
            
        # return None if we can't find the position of the current vehicle
        except ValueError:
            return None
    
    def add_vehicle(self, vehicle: Vehicle) -> bool:
        """
        Method to add a vehicle to the end of the current lane, if the vehicle is allowed in the lane

        :param vehicle: The vehicle we want to add
        """
        # add the given vehicle to the end of the lane
        self._vehicles.append(vehicle)
        self.queue_length += 1
        return True


    def add_vehicle_to_index(self, vehicle: Vehicle, index: int) -> None:
        """ Method do add a vehicle to a specified index """
        self._vehicles.insert(index, vehicle)
        self.queue_length += 1


    def remove_vehicle(self, vehicle: Vehicle) -> Vehicle:
        """
        Removes a given vehicle from the current lane should they enter the box / switch lanes

        :param vehicle: The vehicle we want to remove
        :return: The vehicle removed or None if not found
        """
        # remove a specific vehicle from the list if found
        if vehicle in self._vehicles:
            self._vehicles.remove(vehicle)
            self.queue_length = len(self._vehicles)
            return vehicle
        return None
    
    
    def move_all_vehicles(self, traffic_light_dir: int, update_length_ms: int, box: Box, arm_id: int, lane_id: int) -> Set[Vehicle]:
        """
        Moves all vehicles in the lane based on speed. Cars can move if there is sufficient space
        ahead of them, or if they're at the start of the junction and the light is green

        :param is_light_green: Whether the traffic light for this lane is green or not
        :return: the vehicles currently leaving the junction
        """
        leaving_vehicles = set()
        vehicle_ahead = None

        for i, vehicle in enumerate(self._vehicles):
            # if the vehicles next move will put them in the junction
            if vehicle.get_next_position(update_length_ms) <= 0:
                if self.can_enter_box(vehicle, box, arm_id, lane_id, traffic_light_dir):
                    # this vehicle will leave the junction
                    vehicle.set_source_lane(lane_id)
                    #Move forwards. This allows vehicles to move in both the lane and box in one tick.
                    vehicle.set_position(vehicle.get_next_position(update_length_ms))
                    leaving_vehicles.add(vehicle)

                else:
                    # set distance to 0 if at front of queue, otherwise move forward if space
                    new_vehicle_distance = min(vehicle_ahead.distance + vehicle_ahead.length + vehicle.stopping_distance, vehicle.distance) if vehicle_ahead else 0
                    
                    # update wait time if the vehicle hasn't moved
                    if new_vehicle_distance == vehicle.distance:
                        vehicle.update_wait_time(update_length_ms)

                    # set the new vehicle distance
                    vehicle.set_position(new_vehicle_distance)

            # if the vehicle is at the front of the queue and not at the junction (no need to check vehicle ahead)
            elif i == 0 or vehicle_ahead in leaving_vehicles:
                vehicle.set_position(vehicle.get_next_position(update_length_ms))

            # update vehicle distance if there is enough space to move forward
            elif self.has_space_to_move(vehicle, vehicle_ahead):
                # new position is the furthest the vehicle can travel in the time step ensuring it doesn't get too
                # close to the vehicle ahead
                new_vehicle_distance = max(vehicle.get_next_position(update_length_ms),
                                           vehicle_ahead.distance + vehicle_ahead.length + vehicle.stopping_distance)
                
                vehicle.set_position(new_vehicle_distance)

            # update the wait time if the vehicle doesn't have space to move
            else:
                vehicle.update_wait_time(update_length_ms)

            # update the vehicle ahead for the next iteration
            vehicle_ahead = vehicle

        return leaving_vehicles
        
    def has_space_to_move(self, vehicle: Vehicle, vehicle_ahead: Vehicle) -> bool:
        """ checks if there is any space between a vehicle and the car ahead """
        if vehicle_ahead is None:
            return True
        return vehicle.distance > vehicle_ahead.distance + vehicle_ahead.length + vehicle.stopping_distance
        

    
    def get_earliest_wait_time(self) -> float:
        """
        Method to return the longest wait time currently in the queue. Intuition is the first vehicle will
        always have been waiting for longer than the vehicles behind it as it entered first

        :return: longest wait time present in the lane
        """
        return self._vehicles[0].wait_time if self._vehicles else 0

    def can_enter_box(self, vehicle: Vehicle, box: Box, arm_id: int, lane_id: int, traffic_light_dir: int) -> bool:
        """
        Indicate whether the vehicle in this lane are allowed to enter junction
        i.e. whether cooresponding traffic light is green.
        """
        #If the light is red, do not enter.
        if (arm_id != traffic_light_dir):
            return False

        return self.box_collision_check(vehicle, box, lane_id)

        
    
    def box_collision_check(self, vehicle: Vehicle, box: Box, lane_id: int):
        """
        Returns true if there are no vehicles in the box blocking the path from the given lane to the given vehicles destination
        """
        #Vehicle's relative direction. 1 = right, 2 = forward, 3 = left
        #For more/less arms, represents the number of arms anticlockwise
        vehicle_relative_dir = vehicle.get_relative_direction()

        for box_vehicle in box.get_vehicles():
            box_v_r_d = box_vehicle.get_relative_direction()
            
            #If the box vehicle is from a different arm, it is in a left turn lane and will not cause a collision
            if box_vehicle.source != vehicle.source:
                continue

            #If a vehicle came from a lane to the left
            if box_vehicle.source_lane < lane_id:
                #If the box vehicle is moving somewhere right of the vehicles target, it blocks.
                #Eg: if the box vehicle is moving forwards (2), it blocks left (3) turns.
                if box_v_r_d < vehicle_relative_dir:
                    #print(f"Vehicle in {lane_id} turning {vehicle_relative_dir} blocked by vehicle in {box_vehicle.source_lane} turning {box_v_r_d}")
                    return False

            #If a vehicle came from the right
            elif box_vehicle.source_lane > lane_id:
                #If the box vehicle is moving somewhere right of the vehicles target, it blocks.
                if box_v_r_d > vehicle_relative_dir:
                    #print(f"Vehicle in {lane_id} turning {vehicle_relative_dir} blocked by vehicle in {box_vehicle.source_lane} turning {box_v_r_d}")
                    return False
        #If the light is green and no vehicle in the box blocks it, enter the box
        return True
    
    def create_vehicle(self, speed: int, source: int, destination: int, type: str, start_position: int) -> Vehicle:
        """
        Create a new vehicle, unless forbidden by lane type
        :return: The created vehicle
        """
        if type == "Car":
            v = Car(speed, source, destination, start_position, self._num_arms)
        if type == "Bus":
            v = Bus(speed, source, destination, start_position, self._num_arms)
        if self.can_enter_lane(v):
            self.add_vehicle(v)
            return v
        return None
    
    @abstractmethod
    def can_enter_lane(self, vehicle: Vehicle)-> bool:
        """
        Check if a vehicle is allowed to enter a lane based on type and direction
        :return: True if allowed, false otherwise.
        """


class CarLane(Lane):
    def __init__(self, allowed_directions: Set[int], width: int, length: int, num_arms: int):
        super().__init__(allowed_directions, width, length, num_arms)
        
    
    def can_enter_lane(self, vehicle) -> bool:
        # a vehicle can enter a lane if its going in the intended direction
        return (self._num_arms - vehicle.get_relative_direction()) % self._num_arms in self.allowed_directions


class BusLane(Lane):

    def __init__(self, width: int, length: int, num_arms):
        allowed_directions = {1, 2, 3} # bus lanes can go in every direction
        super().__init__(allowed_directions, width, length, num_arms)
    
    def can_enter_lane(self, vehicle: Vehicle):
        if vehicle.vehicle_type == "Bus":
            return True
        return False

class LeftTurnLane(Lane):

    def __init__(self, width: int, length: int, num_arms: int):
        #The left arm is num_arms - 1 arms anticlockwise from the source arm.
        super().__init__({1}, width, length, num_arms)

    def can_enter_lane(self, vehicle: Vehicle):
        #Can enter only if moving left
        return (self._num_arms - vehicle.get_relative_direction()) % self._num_arms in self.allowed_directions
    
    def can_enter_box(self, vehicle: Vehicle, box: Box, arm_id: int, lane_id: int, traffic_light_dir: int) -> bool:
        #Never enter during a pedestrian crossing
        if traffic_light_dir == -1:
            return False
        if traffic_light_dir == arm_id:
            #If the light is green for all cars do normal collision check
            return self.box_collision_check(vehicle, box, lane_id)
        
        green_light_r_d = (arm_id - traffic_light_dir) % self._num_arms
        #If active arm is immediately to the left, always go as no conflicts can occur
        if  green_light_r_d == self._num_arms - 1:
            #print("Vehicle turned left")
            return True
        else:
            #For other arms, check if a vehicle is turning into the same arm from a different arm
            for v in box.get_vehicles():
                if v.destination == vehicle.destination and v.source != vehicle.source:
                    #print("Vehicle blocked from left turn")
                    return False
        #print("Vehicle turned left from other arm")
        return True


