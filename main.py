#version: 1.0

import pygame
import pygame_gui


from Junction import Junction

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
    "simulation_duration": (300, 650),
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
    relative_rect=pygame.Rect((300, 550), (50, 30)),
    text='Yes',
    manager=manager,
    container=page1_container
)

pedestrian_no = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((300, 580), (50, 30)),
    text='No',
    manager=manager,
    container=page1_container
)

selected_pedestrian = False

# Run simulation
run_simulation_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((900, 700), (150, 50)),
    text='Run Simulation',
    manager=manager,
    container=page1_container
)

# Modify parameters
modify_parameters_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((900, 700), (150, 50)),
    text='Modify Parameters',
    manager=manager,
    container=page2_container
)

table_pos_x = 100
table_pos_y = 100
column_width = 150
row_height = 100

top_junctions = []

output_data = []

def init_table():
    global output_data
    output_data = [
        [''],
        ['Junction\nSpecification'],
        ['Efficiency'],
        ['Average wait time (minutes)'],
        ['Maximum wait time (minutes)'],
        ['Maximum queue length']
    ]

def add_config(efficiency, specification, average_wait, maxmimum_wait, maximum_queue):
    config_number = len(output_data[0])
    output_data[0].append(f'Configuration {config_number}')

    output_data[1].append(specification)
    output_data[2].append(str(efficiency))
    output_data[3].append(str(average_wait))
    output_data[4].append(str(maxmimum_wait))
    output_data[5].append(str(maximum_queue))

def create_table(data):
    for(i,row) in enumerate(output_data):
        for(j,value) in enumerate(row):
            label = pygame_gui.elements.UITextBox(
                html_text=value,
                relative_rect=pygame.Rect(table_pos_x+j*column_width, table_pos_y+i*row_height, column_width, row_height),
                manager=manager,
                container=page2_container
            )

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

        draw_font("Number of lanes\n(e.g. 2-4)", (50, 450))

        draw_font("Include models with\npedestrian crossings", (50, 550))

        draw_font("Crossing time\n(seconds)", (400, 550))

        draw_font("Crossing request\nfrequency (per hour)", (650, 550))

        draw_font("Simulation duration\n(minutes)", (50, 650))

        # event handle
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            manager.process_events(event)

            if event.type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION:
                if event.ui_element == pedestrian_yes:
                    selected_pedestrian = True
                    pedestrian_no.deselect_item('No')
                elif event.ui_element == pedestrian_no:
                    selected_pedestrian = False
                    pedestrian_no.deselect_item('Yes')

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

                elif event.ui_element == run_simulation_button:

                    traffic_data = {}
                    #for input_box in the object of the text input box
                    for key, input_box in traffic_flow_inputs.items():
                        # or 0 to prevent the invalid input
                        traffic_data[key] = int(input_box.get_text() or 0)

                    # not completed yet

                    # params = {}
                    # for key, input_box in param_inputs.items():
                    #     params[key] = int(input_box.get_text() or 0)

                    # for example of junction configurations being with lanes 1-4
                    for i in range(4):

                        # initialise junction, ** is to unpack the dictionary and pass the key-value pair into class
                        junction = Junction(
                            traffic_data,
                            #num_lanes=params["num_lanes"],
                            num_lanes = i+1,
                            pedestrian_crossing = True
                        )

                        print(junction)  # 打印实例化的 Junction 类数据
                        kpi = junction.simulate(5*60*1000, 1000)
                        top_junctions.append(kpi)

                    # top 3 junctions by kpi
                    top_junctions = sorted(top_junctions, reverse=True)[:3]

                    init_table()

                    for junction in top_junctions:
                        add_config(junction,'b',9,9,9)

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

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False


        manager.update(time_delta)
        manager.draw_ui(screen)
        pygame.display.flip()

    elif (game_state == 2):
        pass


pygame.quit()
