# CS261 Group-24
This is our project for the CS261 Coursework: SimuLane. This program calculates key performance metrics such as average and maximum wait times for vehicles at a junction.

Configurable parameters:
    Traffic flow rates: Each cell in the table represents the average number of vehicles per hour travelling between any two arms. The default value is 100 vehicles per hour.

    Number of lanes: The number of lanes in each arm of the junction. Entering two numbers with a hyphen in between (e.g. 2-4) will simulate the junction once for each number in the range. The default value is 3 lanes.

    Pedestrian crossings: If enabled, all traffic lights will be set to red based on the number of requests per hour and the length of the crossing period.
        Crossing time: The length of time pedestrian crossings last in seconds. The default value is 15 seconds.
        Crossing request frequency: The number of crossing requests per hour. When a request is received, the pedestrian crossing will start the next time the lights change. The default value is 10 per hour.
    
    Bus lanes: If enabled, the left most lane will be set as a bus lane which can only have buses in, and buses can be created.
        Bus percentage: The percentage of vehicles that are created as buses. Buses are 10m long and can enter bus lanes. The default value is 1.
    
    Left turn lanes: If enabled, all configurations created must have at least one lane where vehicles can only turn left. In these lanes, vehicles can turn left as long as a pedestrian crossing isn't occuring and no other vehicles are trying to enter the same arm.

    Weightings: Each junction is assigned an efficiency score based on average wait time, maximum wait time and maximum queue length. These weightings determine how much each metric contributes. These values must sum to 1. The default value is 1/3 for each.

    Enabling pedestrian crossings, bus lanes and left turn lanes displays the result as a diagram. Choosing the "Maybe" option results in the junction being simulated with and without the option.

The output screen displays a table of all configurations, sorted by efficiency. The first row shows a diagram representing each lane. The second row shows the overall efficiency and the rest of the table shows the specific values of the key performance indicators. This information is also displayed as a graph for the three most efficient configurations.

To run the program, run the LaneSimulation.exe file in the Executable File folder.
