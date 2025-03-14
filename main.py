# version: 1.0
import pygame
import pygame_gui
import threading
from PIL import Image
from time import time
from Junction import Junction
from exceptions import NotEnoughLanesException, TooManyVehiclesException
from numpy import zeros
import random
import sys
import os
import io
import pkgutil

game_state: int = 0

global crossing_time
global crossing_frequency
global bus_percentage
global lane_configs
global combinations
global traffic_data
global simulation_duration
global top_junctions

# =============Used for Loading capture============
flag = True
counter = 0
counter2 = 0
flipper = True
current_frame = 0
current_frame_car = 0
slow_flipper = True
Maybe = 0

def resource_path(relative_path):
    """Get the absolute path to the resource, works for dev and for PyInstaller"""
    if getattr(sys, 'frozen', False):
        # Running in a PyInstaller bundle
        base_path = sys._MEIPASS
    else:
        # Running in a normal Python environment
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)



gif_path = resource_path("target2.gif")
gif = Image.open(gif_path)
frames = []
while True:
    frame = gif.convert("RGBA")
    pygame_frame = pygame.image.fromstring(frame.tobytes(), frame.size, "RGBA")
    frames.append(pygame_frame)
    try:
        gif.seek(gif.tell() + 1)
    except EOFError:
        break


gif_path = resource_path("target3.gif")
gif = Image.open(gif_path)
frames_car = []
while True:
    frame = gif.convert("RGBA")
    pygame_frame = pygame.image.fromstring(frame.tobytes(), frame.size, "RGBA")
    frames_car.append(pygame_frame)
    try:
        gif.seek(gif.tell() + 1)
    except EOFError:
        break
# =============Used for Loading capture============

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

junction_visualisation = pygame.Surface((300, 300))

# colours
WHITE = (180, 180, 180)
BLACK = (0, 0, 0)
RED = (200, 50, 50)
GREEN = (0, 128, 0)
BLUE = (50, 50, 200)

# word configuration
title = pygame.font.Font(None, 35)
title.set_bold(True)
title.set_italic(True)

font = pygame.font.Font(None, 29)

little_font = pygame.font.Font(None, 23)
little_font.set_italic(True)

bold_font = pygame.font.Font(None, 29)
bold_font.set_bold(True)

symbol = pygame.font.Font(None, 15)
symbol.set_bold(True)


def draw_title(text, position):
    text_surface = title.render(text, True, BLACK, )
    screen.blit(text_surface, position)


def draw_font(text, position):
    text_surface = font.render(text, True, BLACK)
    screen.blit(text_surface, position)


def draw_bold_font_RED(text, position):
    text_surface = bold_font.render(text, True, RED)
    screen.blit(text_surface, position)

def draw_bold_font(text, position):
    text_surface = bold_font.render(text, True, BLACK)
    screen.blit(text_surface, position)


def draw_text(text, position):
    text_surface = symbol.render(text, True, BLACK)
    screen.blit(text_surface, position)


def draw_junction_base(surface):
    surface.fill((200, 200, 200))
    pygame.draw.rect(surface, (50, 50, 50), (100, 0, 100, 300))
    pygame.draw.rect(surface, (50, 50, 50), (0, 100, 300, 100))

    # north
    pygame.draw.line(surface, (255, 255, 255), (150, 0), (150, 100), 2)
    pygame.draw.line(surface, (255, 255, 255), (150, 100), (200, 100), 2)

    # east
    pygame.draw.line(surface, (255, 255, 255), (200, 150), (300, 150), 2)
    pygame.draw.line(surface, (255, 255, 255), (200, 150), (200, 200), 2)

    # south
    pygame.draw.line(surface, (255, 255, 255), (150, 200), (150, 300), 2)
    pygame.draw.line(surface, (255, 255, 255), (100, 200), (150, 200), 2)

    # west
    pygame.draw.line(surface, (255, 255, 255), (0, 150), (100, 150), 2)
    pygame.draw.line(surface, (255, 255, 255), (100, 100), (100, 150), 2)


def draw_junction(surface):
    draw_junction_base(surface)

    bus_lane_shift = 0

    road_font = pygame.font.Font(None, 11)

    if selected_bus != "no":
        bus_lane_shift = 20
        pygame.draw.rect(surface, (155, 17, 30), (180, 0, 20, 100))
        pygame.draw.rect(surface, (155, 17, 30), (202, 180, 100, 20))
        pygame.draw.rect(surface, (155, 17, 30), (100, 202, 20, 100))
        pygame.draw.rect(surface, (155, 17, 30), (0, 100, 100, 20))

    if selected_turn != "no":
        text_n = pygame.transform.rotate(road_font.render("TURN\nLEFT", True, (50, 150, 50)), 180)
        text_e = pygame.transform.rotate(road_font.render("TURN\nLEFT", True, (50, 150, 50)), 90)
        text_s = road_font.render("TURN\nLEFT", True, (50, 150, 50))
        text_w = pygame.transform.rotate(road_font.render("TURN\nLEFT", True, (50, 150, 50)), -90)

        surface.blit(text_n, (180 - bus_lane_shift, 40))
        surface.blit(text_w, (40, 100 + bus_lane_shift))
        surface.blit(text_s, (100 + bus_lane_shift, 240))
        surface.blit(text_e, (240, 180 - bus_lane_shift))

    if selected_pedestrian != "no":
        stripe_width = 5
        gap = 5

        for i in range(11):
            pygame.draw.rect(surface, (255, 255, 255), (95 + i * (stripe_width + gap), 80, stripe_width, 10))
            pygame.draw.rect(surface, (255, 255, 255), (95 + i * (stripe_width + gap), 210, stripe_width, 10))
            pygame.draw.rect(surface, (255, 255, 255), (210, 95 + i * (stripe_width + gap), 10, stripe_width))
            pygame.draw.rect(surface, (255, 255, 255), (80, 95 + i * (stripe_width + gap), 10, stripe_width))

    pygame.draw.circle(surface, (255, 0, 0), (250, 30), 10)
    pygame.draw.circle(surface, (255, 165, 0), (250, 30 + 20), 10)
    pygame.draw.circle(surface, (0, 255,0), (250, 30 + 40), 10)


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
    "num_lanes": (230, 450),
    "crossing_time": (450, 535),
    "crossing_frequency": (760, 535),
    "simulation_duration": (900, 700),
    "bus_percentage": (470, 620),
    "w_avg_wait": (610, 470),
    "w_max_wait": (710, 470),
    "w_queue_len": (815, 470),
}

# Create the object of input box of VPH
traffic_flow_inputs = {}
for key, pos in traffic_flow_positions.items():
    Rectangle = pygame.Rect(pos, (80, 30))

    traffic_flow_inputs[key] = pygame_gui.elements.UITextEntryLine(relative_rect=Rectangle, placeholder_text="vph",
                                                                   manager=manager, container=page1_container)

# Create parameter inputs
param_inputs = {}
for key, pos in param_positions.items():
    Rectangle = pygame.Rect(pos, (80, 30))
    param_inputs[key] = pygame_gui.elements.UITextEntryLine(
        relative_rect=pygame.Rect(pos, (80, 30)),
        manager=manager,
        container=page1_container
    )

pedestrian_yes = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((50, 550), (50, 30)),
    text='Yes',
    manager=manager,
    container=page1_container
)

pedestrian_maybe = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((50 + 60, 550), (80, 30)),
    text='Maybe',
    manager=manager,
    container=page1_container
)

pedestrian_no = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((50 + 150, 550), (50, 30)),
    text='> No <',
    manager=manager,
    container=page1_container
)

turn_yes = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((50, 710), (50, 30)),
    text='Yes',
    manager=manager,
    container=page1_container
)

turn_maybe = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((50 + 60, 710), (80, 30)),
    text='Maybe',
    manager=manager,
    container=page1_container
)

turn_no = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((50 + 150, 710), (50, 30)),
    text='> No <',
    manager=manager,
    container=page1_container
)

bus_yes = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((50, 630), (50, 30)),
    text='Yes',
    manager=manager,
    container=page1_container
)

bus_maybe = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((50 + 60, 630), (80, 30)),
    text='Maybe',
    manager=manager,
    container=page1_container
)

bus_no = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((50 + 150, 630), (50, 30)),
    text='> No <',
    manager=manager,
    container=page1_container
)

selected_pedestrian = "no"
selected_turn = "no"
selected_bus = "no"
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
    relative_rect=pygame.Rect((695, 45), (400, 350)),
    html_text="Errors",
    manager=manager,
    container=page1_container_error,
    visible=False
)

# Modify parameters
modify_parameters_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((5, 5), (80, 50)),
    text='Return',
    manager=manager,
    container=page2_container
)

left_arrow = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect(50, 720, 50, 50),  # Adjust position
    text="<",
    manager=manager,
    container=page2_container,
    visible=False
)

right_arrow = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect(700, 720, 50, 50),  # Adjust position
    text=">",
    manager=manager,
    container=page2_container,
    visible=False
)

# first column of table
start_col = 1

# list of top junctions by efficiency
top_junctions = []

# list of data for table
output_data = []

# list of elements in table
table_elements = []


# update progress bar, full bar contain 99 # symbols


def update_progress_bar(percentage):
    percentage = int(percentage)
    percentage = percentage - 1
    pygame.draw.rect(screen, BLACK, (245, 329, 700, 20), 3)

    bar = ""
    for i in range(0, percentage):
        bar = bar + "#"

    draw_text(bar, (250, 334))
    return


perc_bar = 0


# lower rate, higher speed of increasing of bar. -1 rate for reset bar
def increasing_bar(rate):
    global perc_bar
    if (rate == -1):
        perc_bar = 0
    else:
        if random.random() < rate and perc_bar < 95:
            perc_bar = perc_bar + 1

        update_progress_bar(perc_bar)


def increasing_bar_(rate):
    global perc_bar
    if (rate == -1):
        perc_bar = 0
    else:
        if random.random() < rate and perc_bar < 99:
            perc_bar = perc_bar + 1

        update_progress_bar(perc_bar)


def remove_junction_visualisation():
    global junction_visualisation
    junction_visualisation = None


# list of lane presets which denote which relative dirs each lane can travel in
lane_dir_presets = [
    # all presets for 1 lane configurations
    [[{1, 2, 3}]],

    # all presets for 2 lane configurations
    [[{1}, {2, 3}], [{1, 2}, {3}], [{1}, {1, 2, 3}], [{1, 2, 3}, {3}]],

    # all presets for 3 lane configurations
    [[{1}, {2}, {3}], [{1, 2}, {2}, {2, 3}], [{1}, {2}, {2, 3}], [{1, 2}, {2}, {3}],
     [{1}, {2, 3}, {3}], [{1}, {1, 2}, {3}]],

    # all presets for 4 lane configurations
    [[{1}, {2}, {2}, {3}], [{1}, {2}, {3}, {3}], [{1}, {1}, {2}, {3}], [{1}, {1, 2}, {2, 3}, {3}],
     [{1}, {1, 2}, {2}, {3}], [{1}, {2}, {2, 3}, {3}]],

    # all presets for 5 lane configurations
    [[{1}, {1}, {2}, {3}, {3}], [{1}, {1, 2}, {2}, {2, 3}, {3}], [{1}, {1}, {1}, {2, 3}, {3}],
     [{1}, {1, 2}, {3}, {3}, {3}],
     [{1}, {1}, {2}, {2, 3}, {3}], [{1}, {1, 2}, {2}, {3}, {3}], [{1, 2}, {2}, {2}, {2}, {2, 3}],
     [{1}, {1, 2}, {2}, {2}, {3}], [{1}, {2}, {2}, {2, 3}, {3}]]

]


# setup table data
def init_table():
    global output_data
    output_data = []
    output_data.extend([
        [''],
        ['Junction\nSpecification'],
        ['Efficiency'],
        ['Average wait time (seconds)'],
        ['Maximum wait time (seconds)'],
        ['Maximum queue length'],
        ['Vehicles passed through']
    ])


# add row to table for a configuration
def add_config(efficiency, values, description, passed_per_arm):
    config_number = len(output_data[0])
    output_data[0].append(f'Configuration {config_number}')

    output_data[1].append(description)
    output_data[2].append(str("{:.2f}".format(efficiency)))
    output_data[3].append(
        f"North: {int(values[0][0])}\nEast: {int(values[1][0])}\nSouth: {int(values[2][0])}\nWest: {int(values[3][0])}")
    output_data[4].append(
        f"North: {int(values[0][1])}\nEast: {int(values[1][1])}\nSouth: {int(values[2][1])}\nWest: {int(values[3][1])}")
    output_data[5].append(
        f"North: {int(values[0][2])}\nEast: {int(values[1][2])}\nSouth: {int(values[2][2])}\nWest: {int(values[3][2])}")
    output_data[6].append(
        f"North: {passed_per_arm[0]}\nEast: {passed_per_arm[1]}\nSouth: {passed_per_arm[2]}\nWest: {passed_per_arm[3]}")


# create table with output data
def create_table(data):
    global table_elements

    for element in table_elements:
        element.kill()
    table_elements.clear()

    table_pos_x = 100
    table_pos_y = 50
    column_width = 150
    row_height = 120

    for (i, row) in enumerate(output_data):
        if (i == 0):
            row_height = 45
        elif (i == 1):
            row_height = 170
        elif (i == 2):
            row_height = 45
        else:
            row_height = 120
        label = pygame_gui.elements.UITextBox(
            html_text=row[0],
            relative_rect=pygame.Rect(table_pos_x, table_pos_y, column_width, row_height),
            manager=manager,
            container=page2_container
        )
        table_elements.append(label)
        for j in range(3):
            col_index = start_col + j
            if col_index < len(row):
                if (i != 1):
                    label = pygame_gui.elements.UITextBox(
                        html_text=row[col_index],
                        relative_rect=pygame.Rect(table_pos_x + (j + 1) * column_width, table_pos_y, column_width,
                                                  row_height),
                        manager=manager,
                        container=page2_container
                    )
                    table_elements.append(label)
                else:
                    num_lanes = row[col_index][0]
                    pedestrian = row[col_index][1]
                    bus = row[col_index][2]
                    dirs = row[col_index][3]
                    left = row[col_index][4]

                    junction_surface = pygame.Surface((column_width, row_height))
                    junction_surface.fill((255, 255, 255))

                    pygame.draw.rect(junction_surface, (50, 50, 50), (0, 0, column_width, row_height))

                    lane_width = column_width // (num_lanes)

                    if (bus):
                        pygame.draw.rect(junction_surface, (155, 17, 30), (0, 0, lane_width, row_height))

                    for lane in range(num_lanes - 1):
                        lane_x = lane * lane_width + lane_width
                        pygame.draw.line(junction_surface, (255, 255, 255), (lane_x, 0), (lane_x, row_height), 3)

                    if (pedestrian):
                        stripe_width = 10
                        gap = 10

                        for k in range(9):
                            pygame.draw.rect(junction_surface, (255, 255, 255),
                                             (k * (stripe_width + gap), 20, stripe_width, 20))

                    def draw_arrow(surface, start, end, colour=(255, 255, 255)):
                        pygame.draw.line(surface, colour, start, end, 2)
                        direction = (end[0] - start[0], end[1] - start[1])

                        # draw arrowhead
                        if direction == (0, -15):  # up arrow
                            pygame.draw.polygon(surface, colour, [
                                (end[0] - 4, end[1] + 8),
                                (end[0] + 4, end[1] + 8),
                                (end[0], end[1])
                            ])
                        elif direction == (-15, 0):  # left arrow
                            pygame.draw.polygon(surface, colour, [
                                (end[0] + 8, end[1] - 4),
                                (end[0] + 8, end[1] + 4),
                                (end[0], end[1])
                            ])
                        elif direction == (15, 0):  # right arrow
                            pygame.draw.polygon(surface, colour, [
                                (end[0] - 8, end[1] - 4),
                                (end[0] - 8, end[1] + 4),
                                (end[0], end[1])
                            ])

                    # draw lane arrows
                    for lane in range(num_lanes):
                        lane_x = (lane * lane_width) + (lane_width // 2)  # centre of each lane
                        arrow_y = row_height - 90  # arrow start position

                        if (bus and lane == 0):
                            draw_arrow(junction_surface, (lane_x, arrow_y), (lane_x, arrow_y - 15))
                            draw_arrow(junction_surface, (lane_x, arrow_y), (lane_x - 15, arrow_y))
                            draw_arrow(junction_surface, (lane_x, arrow_y), (lane_x + 15, arrow_y))
                        else:
                            lane_index = lane - 1 if bus else lane  # shift lane index if bus exists

                            if lane_index < len(dirs):
                                if left and dirs[lane_index] == {1}:
                                    draw_arrow(junction_surface, (lane_x, arrow_y), (lane_x - 15, arrow_y), (50, 150, 50))
                                else:
                                    for direction in dirs[lane_index]:
                                        if direction == 2:  # forward
                                            draw_arrow(junction_surface, (lane_x, arrow_y), (lane_x, arrow_y - 15))
                                        if direction == 1:  # left
                                            draw_arrow(junction_surface, (lane_x, arrow_y), (lane_x - 15, arrow_y))
                                        if direction == 3:  # right
                                            draw_arrow(junction_surface, (lane_x, arrow_y), (lane_x + 15, arrow_y))

                    junction_image = pygame_gui.elements.UIImage(
                        relative_rect=pygame.Rect(table_pos_x + (j + 1) * column_width + 2, table_pos_y + 2,
                                                  column_width - 4, row_height - 4),
                        image_surface=junction_surface,
                        manager=manager,
                        container=page2_container
                    )
                    table_elements.append(junction_image)
        table_pos_y += row_height


def show_error_box(error_text):
    error_message_label.set_text(error_text)
    error_message_label.show()


def hide_error_box():
    error_message_label.set_text("")
    error_message_label.visible = False
    error_message_label.hide()


def toggle_button(button_yes, button_maybe, button_no, button_selected):
    draw_junction(junction_visualisation)
    if (button_selected == button_yes):
        button_yes.set_text("> Yes <")
        button_maybe.set_text("Maybe")
        button_no.set_text("No")
    elif (button_selected == button_maybe):
        button_yes.set_text("Yes")
        button_maybe.set_text("> Maybe <")
        button_no.set_text("No")
    else:
        button_yes.set_text("Yes")
        button_maybe.set_text("Maybe")
        button_no.set_text("> No <")


def calc_efficiency(north_arm, south_arm, east_arm, west_arm, w_avg, w_max, w_len) -> float:
    """
    Calculates a junction-wide efficiency, ensuring that if all arms are perfect (zero wait times & zero queue), the overall
    score is 100. This relies on w_avg + w_max + w_queue == 1.
    Each arm is a tuple of (avg_wait, max_wait, max_queue)
    """
    # Scale constants (expected values for each of the metrics)
    avg_wait_scale = 20
    max_wait_scale = 60
    max_queue_scale = 30
    # Gather all arms in a list
    arms = [north_arm, south_arm, east_arm, west_arm]
    # Sum partial scores across the 4 arms
    # Because w_avg + w_max + w_queue = 1, a perfect arm yields 1.0
    # Summing 4 perfect arms => 4. Therefore need to scale to 100 below
    raw_sum = 0.0
    for (avg_wait, max_wait, queue_len) in arms:
        # Weighted sum for this arm
        arm_score = (w_avg * (1.0 / (1.0 + avg_wait/avg_wait_scale))
                     + w_max * (1.0 / (1.0 + max_wait/max_wait_scale))
                     + w_len * (1.0 / (1.0 + queue_len/max_queue_scale))
                     )
        raw_sum += arm_score
    # Perfect sceneario => raw_sum = 4. We want that => 100 => multiply by 25
    total_score = 25.0 * raw_sum
    return total_score


def draw_y_axis():
    # left y-axis
    pygame.draw.line(screen, BLACK, (790, 50), (790, HEIGHT - 50), 2)
    num_ticks = 5
    step = max_value / num_ticks

    for i in range(num_ticks + 1):
        value = int(step * i)
        y_pos = HEIGHT - 50 - (value * scale_factor)
        pygame.draw.line(screen, BLACK, (785, y_pos), (795, y_pos), 2)
        label = font.render(str(value), True, BLACK)
        screen.blit(label, (755, y_pos - 10))


def runSimulation():
    global top_junctions
    start_time = time()
    for num_lanes in lane_configs:
        for (ped_yes, bus_yes, left_yes) in combinations:
            # run each lane configuration
            chosen_lane_presets = num_lanes - 1 if (not bus_yes or num_lanes < 2) else num_lanes - 2
            for lane_directions in lane_dir_presets[chosen_lane_presets]:
                try:
                    # initialise junction, ** is to unpack the dictionary and pass the key-value pair into class
                    junction = Junction(
                        traffic_data,
                        lane_directions,
                        num_lanes=num_lanes,
                        pedestrian_crossing=ped_yes,
                        p_crossing_time_s=crossing_time,
                        p_crossing_freq=crossing_frequency,
                        bus_lane=bus_yes,
                        bus_ratio=bus_percentage,
                        left_turn_lanes=left_yes
                    )

                    # print(junction)

                    junction.simulate(simulation_duration * 60 * 1000, 100)

                    kpi = junction.get_kpi()
                    passed_per_arm = junction.get_arm_throughputs()
                    # print(kpi)
                    top_junctions.append(
                        [calc_efficiency(kpi[0], kpi[1], kpi[2], kpi[3], w_avg, w_max, w_queue), kpi, num_lanes,
                         ped_yes, bus_yes, left_yes, passed_per_arm, lane_directions])

                except NotEnoughLanesException:
                    # Not adding junctions that fail to create
                    pass

    print(f"Simulation duration: {round(time() - start_time, 2)}s")

    # top 3 junctions by kpi
    top_junctions = sorted(top_junctions, key=lambda x: x[0], reverse=True)

    init_table()

    for junction in top_junctions:
        # config_description = f"Lanes: {junction[2]}\nPedestrian crossings: {'Yes' if junction[3] else 'No'}\nBus lanes: {'Yes' if junction[4] else 'No'}\nLeft turn lanes: {'Yes' if junction[5] else 'No'}\n{junction[7]}"
        config_description = [junction[2], junction[3], junction[4], junction[7], junction[5]]
        add_config(junction[0], junction[1], config_description, junction[6])

    return


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

        draw_font("Bus Percentage\n(%)", (300, 615))

        draw_font("Weightings\n(Avg Time / Max Time / Max Queue Length)", (600, 420))

        draw_font("Pedestrian Crossings", (50, 520))

        draw_font("Left turn lane", (50, 680))

        draw_font("Bus lane", (50, 600))

        draw_font("Crossing time\n(seconds)", (300, 535))

        draw_font("Crossing request\nfrequency (per hour)", (550, 535))

        draw_font("Simulation duration\n(minutes)", (700, 700))

        if(selected_pedestrian == "maybe" or selected_bus == "maybe" or selected_turn == "maybe"):
            draw_bold_font_RED("WARNING: The maybe option significantly increases running time", (500, 665))

        junction_visualisation.fill((255, 255, 255))
        draw_junction(junction_visualisation)
        screen.blit(junction_visualisation, (700, 50))

        # event handle
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            manager.process_events(event)

            # click on button event
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == pedestrian_yes:
                    selected_pedestrian = "yes"
                    toggle_button(pedestrian_yes, pedestrian_maybe, pedestrian_no, pedestrian_yes)
                elif event.ui_element == pedestrian_maybe:
                    selected_pedestrian = "maybe"
                    toggle_button(pedestrian_yes, pedestrian_maybe, pedestrian_no, pedestrian_maybe)
                elif event.ui_element == pedestrian_no:
                    selected_pedestrian = "no"
                    toggle_button(pedestrian_yes, pedestrian_maybe, pedestrian_no, pedestrian_no)

                elif event.ui_element == bus_yes:
                    selected_bus = "yes"
                    toggle_button(bus_yes, bus_maybe, bus_no, bus_yes)
                elif event.ui_element == bus_maybe:
                    selected_bus = "maybe"
                    toggle_button(bus_yes, bus_maybe, bus_no, bus_maybe)
                elif event.ui_element == bus_no:
                    selected_bus = "no"
                    toggle_button(bus_yes, bus_maybe, bus_no, bus_no)

                elif event.ui_element == turn_yes:
                    selected_turn = "yes"
                    toggle_button(turn_yes, turn_maybe, turn_no, turn_yes)
                elif event.ui_element == turn_maybe:
                    selected_turn = "maybe"
                    toggle_button(turn_yes, turn_maybe, turn_no, turn_maybe)
                elif event.ui_element == turn_no:
                    selected_turn = "no"
                    toggle_button(turn_yes, turn_maybe, turn_no, turn_no)

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

                        if not value:
                            input_box.set_text("100")
                            traffic_data[key] = 100
                        elif not value.isdigit() or not (0 <= int(value) <= 3000):
                            traffic_flow_rates_invalid = True
                        else:
                            traffic_data[key] = int(value)

                    if traffic_flow_rates_invalid:
                        error_messages.append(
                            "Error: All traffic flow rates must be integer values between 0 and 3000.")
                    else:
                        row1 = [0, traffic_data["n2e"], traffic_data["n2s"], traffic_data["n2w"]]
                        row2 = [traffic_data["e2n"], 0, traffic_data["e2s"], traffic_data["e2w"]]
                        row3 = [traffic_data["s2n"], traffic_data["s2e"], 0, traffic_data["s2w"]]
                        row4 = [traffic_data["w2n"], traffic_data["w2e"], traffic_data["w2s"], 0]
                        traffic_data = [row1, row2, row3, row4]

                    # ------------------------------------------------------------------------------------------------------------------
                    # validate number of lanes input
                    num_lanes_input = param_inputs["num_lanes"].get_text().strip()
                    if not num_lanes_input:
                        param_inputs["num_lanes"].set_text("3")
                        lane_configs = [3]
                    else:
                        if "-" in num_lanes_input:
                            parts = num_lanes_input.split("-")
                            if len(parts) != 2 or not all(p.isdigit() for p in parts):
                                num_lanes_invalid = True
                            else:
                                start = int(parts[0])
                                end = int(parts[1])
                                if not (1 <= start < end <= 5):
                                    num_lanes_invalid = True
                                else:
                                    lane_configs = list(range(start, end + 1))
                        else:
                            if not num_lanes_input.isdigit():
                                num_lanes_invalid = True
                            else:
                                num_lanes_input = int(num_lanes_input)
                                if not (1 <= num_lanes_input <= 5):
                                    num_lanes_invalid = True
                                else:
                                    lane_configs = [num_lanes_input]

                    if num_lanes_invalid:
                        error_messages.append(
                            "Error: Number of lanes must be in format X or X-Y where the range of lanes is 1-5.")

                    # ------------------------------------------------------------------------------------------------------------------
                    # Initialise crossing values as None
                    crossing_frequency = None
                    crossing_time = None
                    # validate pedestrian crossing details
                    if selected_pedestrian != "no":
                        crossing_time_input = param_inputs["crossing_time"].get_text().strip()
                        crossing_frequency_input = param_inputs["crossing_frequency"].get_text().strip()

                        if not crossing_time_input.isdigit() or int(crossing_time_input) <= 0:
                            pedestrian_details_invalid = True
                        if not crossing_frequency_input.isdigit() or int(crossing_frequency_input) <= 0:
                            pedestrian_details_invalid = True
                        if (not pedestrian_details_invalid):
                            crossing_time = int(crossing_time_input)
                            crossing_frequency = int(crossing_frequency_input)
                        if (not crossing_time_input and not crossing_frequency_input):
                            pedestrian_details_invalid = False
                        if (not crossing_time_input):
                            param_inputs["crossing_time"].set_text("15")
                            crossing_time = 10
                        if (not crossing_frequency_input):
                            param_inputs["crossing_frequency"].set_text("10")
                            crossing_frequency = 30
                           

                    if pedestrian_details_invalid:
                        error_messages.append(
                            "Error: Crossing time and crossing frequency request must be filled in with integer values.")

                    # ------------------------------------------------------------------------------------------------------------------
                    # validate simulation duration
                    simulation_duration_input = param_inputs["simulation_duration"].get_text().strip()
                    if not simulation_duration_input or not simulation_duration_input.isdigit() or int(
                            simulation_duration_input) <= 0 or int(simulation_duration_input) >= 1000:
                        simulation_duration_invalid = True

                    if simulation_duration_invalid:
                        if not simulation_duration_input:
                            param_inputs["simulation_duration"].set_text("60")
                        else:
                            error_messages.append("Error: Simulation duration must be a positive integer less than 1000.")
                    simulation_duration_input = param_inputs["simulation_duration"].get_text().strip()
                    simulation_duration = int(simulation_duration_input)

                    # ------------------------------------------------------------------------------------------------------------------
                    # validate bus percentage
                    bus_percentage_input = param_inputs["bus_percentage"].get_text().strip()
                    if selected_bus != "no":
                        try:
                            if not bus_percentage_input.isdigit() or not (0 <= int(bus_percentage_input) <= 100):
                                bus_percentage_invalid = True
                            else:
                                bus_percentage = float(bus_percentage_input)
                        except ValueError:
                            bus_percentage_invalid = True

                    if bus_percentage_invalid:
                        if not bus_percentage_input:
                            param_inputs["bus_percentage"].set_text("1")
                            bus_percentage = 1
                        else:
                            error_messages.append("Error: Bus percentage must be an integer between 0 and 100.")

                    # validate KPI weightings
                    w_avg_input = param_inputs["w_avg_wait"].get_text().strip()
                    w_max_input = param_inputs["w_max_wait"].get_text().strip()
                    w_queue_input = param_inputs["w_queue_len"].get_text().strip()

                    weightings_invalid = False
                    w_avg = w_max = w_queue = 0.0

                    try:
                        if (w_avg_input == "" and w_max_input == "" and w_queue_input == ""):
                            w_avg = 0.3333
                            param_inputs["w_avg_wait"].set_text("0.3333")
                            w_max = 0.3333
                            param_inputs["w_max_wait"].set_text("0.3333")
                            w_queue = 0.3334
                            param_inputs["w_queue_len"].set_text("0.3334")
                        else:
                            w_avg = float(w_avg_input)
                            w_max = float(w_max_input)
                            w_queue = float(w_queue_input)
                        # Each weighting must be between 0 and 1 (inclusive)
                        if not (0 <= w_avg <= 1 and 0 <= w_max <= 1 and 0 <= w_queue <= 1):
                            weightings_invalid = True
                        # They must sum to exactly 1 (allow a tiny float tolerance)
                        total_weight = w_avg + w_max + w_queue
                        if abs(total_weight - 1.0) > 1e-9:
                            weightings_invalid = True
                    except ValueError:
                        weightings_invalid = True

                    if weightings_invalid:
                        error_messages.append(
                            "Error: The weightings for Average Waiting Time, Max Waiting Time and Max Queue Length must be valid floats between 0 and 1 with the sum of the three being 1"
                        )
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

                    if selected_pedestrian == "yes":
                        ped = [True]
                    elif selected_pedestrian == "maybe":
                        Maybe = Maybe + 1
                        ped = [False, True]
                    else:
                        ped = [False]

                    if selected_bus == "yes":
                        bus = [True]
                    elif selected_bus == "maybe":
                        Maybe = Maybe + 1
                        bus = [False, True]
                    else:
                        bus = [False]

                    if selected_turn == "yes":
                        left = [True]
                    elif selected_turn == "maybe":
                        Maybe = Maybe + 1
                        left = [False, True]
                    else:
                        left = [False]

                    combinations = [(x, y, z) for x in ped for y in bus for z in left]

                    game_state = 2

        # update gui, flip the screen
        manager.update(time_delta)
        manager.draw_ui(screen)
        pygame.display.flip()

    elif (game_state == 1):

        screen.fill(WHITE)

        page1_container.hide()
        page2_container.show()

        screen.blit(font.render("Bus lane", True, (155, 17, 30)), (10, 100))
        screen.blit(font.render("Left turn\nlane", True, (50, 150, 50)), (10, 120))
        screen.blit(font.render("Regular\nlane", True, (50, 50, 50)), (10, 160))

        left_arrow.hide()
        right_arrow.hide()

        if (len(top_junctions) > 3):
            left_arrow.show()
            right_arrow.show()

        create_table(output_data)

        data = {}

        for i in range(min(3, len(top_junctions))):
            kpi = top_junctions[i][1]
            avg_wait = (kpi[0][0] + kpi[1][0] + kpi[2][0] + kpi[3][0]) / 4
            max_wait = max(kpi[0][1], kpi[1][1], kpi[2][1], kpi[3][1])
            max_queue = max(kpi[0][2], kpi[1][2], kpi[2][2], kpi[3][2])
            data[(f"Config {i + 1}")] = (avg_wait, max_wait, max_queue)

        bar_width = 20
        bar_gap = 5
        cluster_gap = (bar_width + bar_gap) * 3 + 30
        start_x = 800

        chart_height = HEIGHT - 220
        max_value = max(max(values) for values in data.values())
        scale_factor = (HEIGHT - 220) / max_value if max_value != 0 else 1

        draw_y_axis()

        x = start_x
        for config, (avg_wait, max_wait, max_queue) in data.items():
            avg_h = avg_wait * scale_factor
            max_h = max_wait * scale_factor
            queue_h = max_queue * scale_factor

            pygame.draw.rect(screen, BLUE, (x, HEIGHT - 50 - avg_h, bar_width, avg_h))
            pygame.draw.rect(screen, RED, (x + bar_width + bar_gap, HEIGHT - 50 - max_h, bar_width, max_h))
            pygame.draw.rect(screen, GREEN, (x + 2 * (bar_width + bar_gap), HEIGHT - 50 - queue_h, bar_width, queue_h))

            text = font.render(config, True, BLACK)
            screen.blit(text, (x + bar_width - text.get_width() / 2 + 20, HEIGHT - 40))

            x += cluster_gap

        screen.blit(font.render("Avg. Wait Time (s)", True, BLUE), (1000, 50))
        screen.blit(font.render("Max. Wait Time (s)", True, RED), (1000, 80))
        screen.blit(font.render("Max. Queue Length\n(vehicles)", True, GREEN), (1000, 110))

        manager.process_events(event)
        # click on button event
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == left_arrow and start_col > 1:
                start_col -= 1
                create_table(output_data)

            elif event.ui_element == right_arrow and start_col + 3 < len(output_data[0]):
                start_col += 1
                create_table(output_data)
            elif event.ui_element == modify_parameters_button:
                top_junctions = []
                game_state = 0
                start_col = 1
                flag = True
                hide_error_box()
                init_table()

                for element in table_elements:
                    element.kill()
                table_elements.clear()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # flip the screen
        manager.update(time_delta)
        manager.draw_ui(screen)
        pygame.display.flip()

    elif (game_state == 2):
        if flag:
            thread = threading.Thread(target=runSimulation)
            thread.start()
            flag = False

        screen.fill(WHITE)
        page1_container.hide()
        page2_container.hide()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            manager.process_events(event)

        mouse_x, mouse_y = pygame.mouse.get_pos()
        coord_text = little_font.render(f"Mouse Position: ({mouse_x}, {mouse_y})", True, BLACK)
        screen.blit(coord_text, (800, 10))

        # some calculation here
        # 0.1441 for 12s
        # 0.2841 for 6s
        # this is a inverse proportional function, approximately linear
        sum_traffic = sum(sum(row) for row in traffic_data)

        def factorial(n):
            if n == 0 or n == 1:
                return 1
            else:
                return n * factorial(n - 1)
        maybeFactor = factorial(Maybe+1)
        # experience formula
        estimate_time = (max([1, sum_traffic * 0.001029])) * (sum(lane_configs) * 0.53) * (simulation_duration * 0.0328) * maybeFactor

        rate = (1 / estimate_time) * 1.7139
        increasing_bar(rate)

        if counter % 80 != 0:
            counter = counter + 1
        else:
            counter = counter + 1
            flipper = not flipper

        if counter % 2 == 0:
            slow_flipper = not slow_flipper

        if flipper:

            draw_title("Loading.....", (400, 303))

        else:

            draw_title("Loading....", (400, 303))

        if slow_flipper:
            current_frame = (current_frame + 1) % len(frames)
            current_frame_car = (current_frame_car + 1) % len(frames_car)

        screen.blit(frames[current_frame], (514, 379))
        screen.blit(frames_car[current_frame_car], (590, 238))

        if (thread.is_alive()):
            pass
        else:
            if counter2 < 200:
                increasing_bar_(0.9)
                counter2 = counter2 + 1
            else:

                # returning to input page if there are no valid junctions
                if (len(top_junctions) == 0):
                    top_junctions = []
                    game_state = 0
                    counter2 = 0

                    Maybe = 0
                    flag = True
                    init_table()
                    show_error_box("Not enough lanes to model any specified junction.")
                else:
                    increasing_bar(-1)

                    Maybe = 0
                    counter2 = 0
                    game_state = 1

        # flip the screen
        manager.update(time_delta)
        manager.draw_ui(screen)
        pygame.display.flip()

pygame.quit()
