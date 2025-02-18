#version: 1.0

import pygame
import pygame_gui

from time import time
from Junction import Junction
import math
game_state:int = 0



pygame.init()

# window size
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Traffic Junction Simulation")

# GUI manager
manager = pygame_gui.UIManager((WIDTH, HEIGHT))

page1_container = pygame_gui.core.UIContainer(relative_rect=pygame.Rect((0, 0), (WIDTH, HEIGHT)), manager=manager)
page2_container = pygame_gui.core.UIContainer(relative_rect=pygame.Rect((0, 0), (WIDTH, HEIGHT)), manager=manager)

page1_container_error = pygame_gui.core.UIContainer(relative_rect=pygame.Rect((0, 0), (WIDTH, HEIGHT)), manager=manager)

# color
WHITE = (180, 180, 180)
BLACK = (0, 0, 0)

# word configuration
title = pygame.font.Font(None, 35)
title.set_bold(True)
title.set_italic(True)

font = pygame.font.Font(None, 29)

little_font = pygame.font.Font(None, 23)
little_font.set_italic(True)

bold_font = pygame.font.Font(None, 29)
bold_font.set_bold(True)

def draw_title(text, position):
    text_surface = title.render(text, True, BLACK, )
    screen.blit(text_surface, position)

def draw_font(text, position):
    text_surface = font.render(text, True, BLACK)
    screen.blit(text_surface, position)

def draw_bold_font(text, position):
    text_surface = bold_font.render(text, True, BLACK)
    screen.blit(text_surface, position)


traffic_flow_positions = {
    "n2e": (250, 110),
    "n2s": (370, 110),
    "n2w": (490, 110),
    "e2n": (130, 180),
    "e2s": (370, 180),
    "e2w": (490, 180),
    "s2e": (250, 250),
    "s2n": (130, 250),
    "s2w": (490, 250),
    "w2n": (130, 320),
    "w2s": (370, 320),
    "w2e": (250, 320),
}


param_positions = {
    "num_lanes": (300, 450),
    "crossing_time": (550, 550),
    "crossing_frequency": (850, 550),
    "simulation_duration": (622, 450),
    "bus_percentage": (709, 741),
}


# Create the object of input box of VPH
traffic_flow_inputs = {}
for key, pos in traffic_flow_positions.items():
    Rectangle = pygame.Rect(pos, (80, 30))

    traffic_flow_inputs[key] = pygame_gui.elements.UITextEntryLine(relative_rect=Rectangle, placeholder_text="vph", manager=manager, container=page1_container)

# other input box, not completed
param_inputs = {}
for key, pos in param_positions.items():
    Rectangle = pygame.Rect(pos, (80, 30))
    param_inputs[key] = pygame_gui.elements.UITextEntryLine(
        relative_rect=pygame.Rect(pos, (80, 30)),
        manager=manager,
        container=page1_container
    )

# yes or no button

pedestrian_yes = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((82, 703-40), (50, 30)),
    text='Yes',
    manager=manager,
    container=page1_container
)

pedestrian_no = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((82+60, 703-40), (50, 30)),
    text='No',
    manager=manager,
    container=page1_container
)

turn_yes = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((380, 703-40), (50, 30)),
    text='Yes',
    manager=manager,
    container=page1_container
)

turn_no = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((380+60, 703-40), (50, 30)),
    text='No',
    manager=manager,
    container=page1_container
)

bus_yes = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((685, 703-40), (50, 30)),
    text='Yes',
    manager=manager,
    container=page1_container
)

bus_no = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((685+60, 703-40), (50, 30)),
    text='No',
    manager=manager,
    container=page1_container
)

selected_pedestrian = False
selected_turn = False
selected_bus = False
bus_percentage = 0


# Run simulation
run_simulation_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((1020, 700), (150, 70)),
    text='Run Simulation',
    manager=manager,
    container=page1_container
)

# error message box
error_message_label = pygame_gui.elements.UITextBox(
    relative_rect=pygame.Rect((700, 50), (400, 200)),
    html_text="Errors",
    manager=manager,
    container=page1_container_error,
    visible=False
)



# Modify parameters
modify_parameters_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((900, 700), (150, 50)),
    text='Modify Parameters',
    manager=manager,
    container=page2_container
)

table_pos_x = 100
table_pos_y = 50
column_width = 150
row_height = 120

top_junctions = []

output_data = []

table_elements = []

def init_table():
    global output_data
    output_data = []
    output_data.extend([
        [''],
        ['Junction\nSpecification'],
        ['Efficiency'],
        ['Average wait time (seconds)'],
        ['Maximum wait time (seconds)'],
        ['Maximum queue length']
    ])

def add_config(efficiency, values, description):
    config_number = len(output_data[0])
    output_data[0].append(f'Configuration {config_number}')

    output_data[1].append(description)
    output_data[2].append(str((int)(efficiency)))
    output_data[3].append(f"North: {(int)(values[0][0])}\nEast: {(int)(values[1][0])}\nSouth: {(int)(values[2][0])}\nWest: {(int)(values[3][0])}")
    output_data[4].append(f"North: {(int)(values[0][1])}\nEast: {(int)(values[1][1])}\nSouth: {(int)(values[2][1])}\nWest: {(int)(values[3][1])}")
    output_data[5].append(f"North: {(int)(values[0][2])}\nEast: {(int)(values[1][2])}\nSouth: {(int)(values[2][2])}\nWest: {(int)(values[3][2])}")

def create_table(data):
    for(i,row) in enumerate(output_data):
        for(j,value) in enumerate(row):
            label = pygame_gui.elements.UITextBox(
                html_text=value,
                relative_rect=pygame.Rect(table_pos_x+j*column_width, table_pos_y+i*row_height, column_width, row_height),
                manager=manager,
                container=page2_container
            )
            table_elements.append(label)

def show_error_box(error_text):
    error_message_label.set_text(error_text)
    error_message_label.show()

def hide_error_box():
    error_message_label.set_text("")
    error_message_label.visible=False
    error_message_label.hide()

def calc_efficiency(north_arm, south_arm, east_arm, west_arm) -> int:
    total_score = 0
    arms = [north_arm, south_arm, east_arm, west_arm]

    for arm_data in arms:
        avg_wait, max_wait, max_queue = arm_data
        # compute partial score
        arn_score = 0
        try:
            arm_score = (100/avg_wait) + (100/max_wait) + (100/max_queue)
        except ZeroDivisionError:
            arm_score = 100
        # add to the total score for the junction
        total_score += arm_score
    return total_score

# 0 is for initial page
game_state = 0
clock = pygame.time.Clock()
running = True

while running:
    # set the simulation FPS as 60
    # this function will return the time interval between this frame and previous frame in ms
    # it should be 16.67 ms (60 frame per second) if not lag
    # ----um my cursor flashing in 60fps so I just changed it to 240, dont mind it
    time_delta = clock.tick(240)


    if (game_state == 0):
        page2_container.hide()
        page1_container.show()


        screen.fill(WHITE)

        mouse_x, mouse_y = pygame.mouse.get_pos()
        coord_text = little_font.render(f"Mouse Position: ({mouse_x}, {mouse_y})", True, BLACK)
        screen.blit(coord_text, (800, 10))

        # draw text
        draw_title("Traffic flow rates", (200, 5))
        draw_font("North", (50, 125))
        draw_font("East", (50, 185))
        draw_font("South", (50, 255))
        draw_font("West", (50, 325))

        draw_font("North", (145, 75))
        draw_font("East", (270, 75))
        draw_font("South", (395, 75))
        draw_font("West", (510, 75))

        draw_bold_font("Out", (70, 45))
        draw_bold_font("In", (50, 85))
        pygame.draw.line(screen, BLACK, (15, 45), (125, 110), 4)


        draw_title("Configurable parameters", (50, 400))

        draw_font("Number of lanes\n(e.g. 2-5)", (50, 450))

        draw_font("Bus Percentage (input 0 to 1)", (656, 710))

        draw_font("Pedestrian Crossings", (50, 630))

        draw_font("Trun Lane", (385, 630))

        draw_font("Bus Lane", (695, 630))

        draw_font("Crossing time\n(seconds)", (400, 550))

        draw_font("Crossing request\nfrequency (per hour)", (650, 550))

        draw_font("Simulation duration\n(minutes)", (403, 450))

        # event handle
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            manager.process_events(event)

            # click on button event
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == pedestrian_yes:
                    selected_pedestrian = True
                    pedestrian_yes.set_text("> Yes <")
                    pedestrian_no.set_text("No")
                elif event.ui_element == pedestrian_no:
                    selected_pedestrian = False
                    pedestrian_yes.set_text("Yes")
                    pedestrian_no.set_text("> No <")

                elif event.ui_element == bus_yes:
                    selected_bus = True
                    bus_yes.set_text("> Yes <")
                    bus_no.set_text("No")
                elif event.ui_element == bus_no:
                    selected_bus = False
                    bus_yes.set_text("Yes")
                    bus_no.set_text("> No <")

                elif event.ui_element == turn_yes:
                    selected_turn = True
                    turn_yes.set_text("> Yes <")
                    turn_no.set_text("No")
                elif event.ui_element == turn_no:
                    selected_turn = False
                    turn_yes.set_text("Yes")
                    turn_no.set_text("> No <")



                elif event.ui_element == run_simulation_button:

                    traffic_data = {}
                    lane_configs = []

                    traffic_flow_rates_invalid = False
                    num_lanes_invalid = False
                    pedestrian_details_invalid = False
                    simulation_duration_invalid = False
                    bus_percentage_invalid = False

                    error_messages = []



                    # validate traffic flow rates
                    for key, input_box in traffic_flow_inputs.items():
                        value = input_box.get_text().strip()

                        if not value.isdigit() or not (0 <= int(value) <= 3000):
                            traffic_flow_rates_invalid = True
                        else:
                            traffic_data[key] = int(value)

                    if traffic_flow_rates_invalid:
                        error_messages.append("Error: All traffic flow rates must be integer values between 0 and 3000.")

                    print(traffic_data)
                    row1 = [-1,traffic_data["n2e"],traffic_data["n2s"],traffic_data["n2w"]]
                    row2 = [traffic_data["e2n"],-1,  traffic_data["e2s"], traffic_data["e2w"]]
                    row3 = [traffic_data["s2n"], traffic_data["s2e"],-1,  traffic_data["s2w"]]
                    row4 = [traffic_data["w2n"], traffic_data["w2e"], traffic_data["w2s"], -1]
                    top_junctions = [row1, row2, row3, row4]
                    print(top_junctions)
                    #------------------------------------------------------------------------------------------------------------------
                    # validate number of lanes input
                    num_lanes_input = param_inputs["num_lanes"].get_text().strip()
                    if not num_lanes_input:
                        num_lanes_invalid = True
                    else:
                        if "-" in num_lanes_input:
                            parts = num_lanes_input.split("-")
                            if len(parts) != 2 or not all(p.isdigit() for p in parts):
                                num_lanes_invalid = True
                            else:
                                start = int(parts[0])
                                end = int(parts[1])
                                if not(1 <= start < end <= 5):
                                    num_lanes_invalid = True
                                else:
                                    lane_configs = list(range(start, end + 1))
                        else:
                            if not num_lanes_input.isdigit():
                                num_lanes_invalid = True
                            else:
                                num_lanes_input = int(num_lanes_input)
                                if not (1 <= num_lanes_input <=5):
                                    num_lanes_invalid = True
                                else:
                                    lane_configs = [num_lanes_input]

                    if num_lanes_invalid:
                        error_messages.append("Error: Number of lanes must be in format X or X-Y where the range of lanes is 1-5.")

                    # ------------------------------------------------------------------------------------------------------------------
                    #Initialise crossing values as None
                    crossing_frequency = None
                    crossing_time = None
                    # validate pedestrian crossing details
                    if selected_pedestrian:
                        crossing_time_input = param_inputs["crossing_time"].get_text().strip()
                        crossing_frequency_input = param_inputs["crossing_frequency"].get_text().strip()

                        if not crossing_time_input.isdigit() or int(crossing_time_input) <= 0:
                            pedestrian_details_invalid = True

                        if not crossing_frequency_input.isdigit() or int(crossing_frequency_input) <= 0:
                            pedestrian_details_invalid = True
                        if (not pedestrian_details_invalid):
                            crossing_time = int(crossing_time_input)
                            crossing_frequency = int(crossing_frequency_input)

                    if pedestrian_details_invalid:
                        error_messages.append("Error: Crossing time and crossing frequency request must be filled in with integer values.")

                    # ------------------------------------------------------------------------------------------------------------------
                    # validate simulation duration
                    simulation_duration_input = param_inputs["simulation_duration"].get_text().strip()
                    if not simulation_duration_input or not simulation_duration_input.isdigit() or int(simulation_duration_input) <= 0:
                        simulation_duration_invalid = True
                    
                    if simulation_duration_invalid:
                        error_messages.append("Error: Simulation duration must be a positive integer.")
                    else:
                        simulation_duration = int(simulation_duration_input)

                    # ------------------------------------------------------------------------------------------------------------------
                    # validate bus percentage
                    bus_percentage_input = param_inputs["bus_percentage"].get_text().strip()
                    if bus_percentage_input:
                        if bus_percentage_input.isdigit():
                            if (float(bus_percentage_input) < 0) or (float(bus_percentage_input) > 1):
                                bus_percentage_invalid = True
                        else:

                            bus_percentage_invalid = True

                    if bus_percentage_invalid:
                        error_messages.append("Error: Bus percentage must be a number within 0 to 1.")

                    # ------------------------------------------------------------------------------------------------------------------
                    # display error
                    if error_messages:
                        show_error_box("\n".join(error_messages))
                        continue
                    else:
                        hide_error_box()


                    '''
                    selected_turn : boolean
                    selected_bus : boolean
                    input box is implemented in front end, the result will be store in these two var.
                    
                    bus_percentage_input : str
                    percentage of bus, note that this is string type.
                    '''



                    for num_lanes in lane_configs:

                        # initialise junction, ** is to unpack the dictionary and pass the key-value pair into class
                        junction = Junction(
                            top_junctions,
                            num_lanes = num_lanes,
                            pedestrian_crossing = selected_pedestrian,
                            p_crossing_time_s = crossing_time,
                            p_crossing_freq = crossing_frequency,
                            bus_lane = selected_bus
                        )

                        print(junction)
                        start_time = time()
                        junction.simulate(simulation_duration*60*1000, 100)
                        print(f"Simulation duration: {time() - start_time}")
                        kpi = junction.get_kpi()
                        top_junctions.append([calc_efficiency(kpi[0], kpi[1], kpi[2], kpi[3]), kpi, num_lanes])


                    # top 3 junctions by kpi
                    top_junctions = sorted(top_junctions, key=lambda x: x[0], reverse=True)[:3]

                    init_table()

                    for junction in top_junctions:
                        config_description = f"{junction[2]} lanes\nPedestrian crossings: {'Yes' if selected_pedestrian else 'No'}"
                        add_config(junction[0],junction[1],config_description)

                    create_table(output_data)

                    game_state = 1

        # update gui, flip the screen
        manager.update(time_delta)
        manager.draw_ui(screen)
        pygame.display.flip()

    elif(game_state == 1):

        screen.fill(WHITE)

        page1_container.hide()
        page2_container.show()

        create_table(output_data)

        mouse_x, mouse_y = pygame.mouse.get_pos()
        coord_text = little_font.render(f"Mouse Position: ({mouse_x}, {mouse_y})", True, BLACK)
        screen.blit(coord_text, (800, 10))

        manager.process_events(event)
        # click on button event
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == modify_parameters_button:
                game_state = 0
                hide_error_box()
                init_table()

                for element in table_elements:
                    element.kill()
                table_elements.clear()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False


        manager.update(time_delta)
        manager.draw_ui(screen)
        pygame.display.flip()

    elif (game_state == 2):
        pass


pygame.quit()
