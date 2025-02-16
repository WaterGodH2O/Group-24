from Arm import Arm
from Lane import CarLane
from Vehicle import Car

# !!! comment out anything related to box junctions to ensure this test is valid and replace self.can_enter_box with is_light_green in Lane.py

# create a new lane with the following parameters:
    # width 30m, length 100m, vph 50 50 50, 3 lanes
arm = Arm(30, 100, [50, 50, 50, 0], 3)

lanes = arm._lanes

# add 3 vehicles to each lane as a test (coming from west)
car1 = Car(3, 3, 0, 0, 5)
lanes[0].add_vehicle(car1)
lanes[0].add_vehicle(Car(3, 3, 0, 2.1, 7))
lanes[0].add_vehicle(Car(3, 3, 0, 5, 9))

car2 = Car(3, 3, 1, 1, 5)
lanes[1].add_vehicle(car2)
lanes[1].add_vehicle(Car(3, 3, 1, 2.2, 7))
lanes[1].add_vehicle(Car(3, 3, 1, 5, 9))

car3 = Car(3, 3, 2, 0, 5)
lanes[2].add_vehicle(car3)
lanes[2].add_vehicle(Car(3, 3, 2, 2.5, 7))
lanes[2].add_vehicle(Car(3, 3, 2, 10, 9))


print(len(arm._lanes))



""" TEST LANE MOVEMENT -> set to True if want to test with green lights """
arm.move_all_vehicles(10000, False, None, 1000, 0)


# check if car 1 is still in lane 0
if car1 in lanes[0]._vehicles:
    print("CAR 1 IS STILL IN THE LANE!!!")
else:
    print("CAR 1 HAS SUCCFULLY LEFT THE LANE")

# check if car 1 is still in lane 0
if car2 in lanes[1]._vehicles:
    print("CAR 2 IS STILL IN THE LANE!!!")
else:
    print("CAR 2 HAS SUCCFULLY LEFT THE LANE")


if car3 in lanes[2]._vehicles:
    print("CAR 3 IS STILL IN THE LANE!!!")
else:
    print("CAR 3 HAS SUCCFULLY LEFT THE LANE")


for lane in lanes:
    print("\n")
    for vehicle in lane._vehicles:
        print(f"Vehicle distance: {vehicle.distance} | Vehicle speed: {vehicle._speed} | Stopping distance: {vehicle._stopping_distance}")


print(f"\nKPI: {arm.get_kpi()}")