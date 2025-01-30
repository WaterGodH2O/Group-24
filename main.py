import pygame
import pygame_gui


from Junction import Junction

game_state:int = 0



pygame.init()

# window size
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Traffic Junction Simulation")

# 创建 GUI 管理器
manager = pygame_gui.UIManager((WIDTH, HEIGHT))

# 颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# word configuration
title = pygame.font.Font(None, 35)
title.set_bold(True)
title.set_italic(True)

font = pygame.font.Font(None, 29)

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
    "num_lanes": (400, 650),
    "crossing_time": (650, 650),
    "crossing_frequency": (900, 650),
    "simulation_duration": (400, 700),
}

# Create the object of input box of VPH
traffic_flow_inputs = {}
for key, pos in traffic_flow_positions.items():
    Rectangle = pygame.Rect(pos, (80, 30))

    traffic_flow_inputs[key] = pygame_gui.elements.UITextEntryLine(relative_rect=Rectangle, manager=manager)

# other input box, not completed
param_inputs = {}
for key, pos in param_positions.items():
    Rectangle = pygame.Rect(pos, (80, 30))
    param_inputs[key] = pygame_gui.elements.UITextEntryLine(
        relative_rect=pygame.Rect(pos, (80, 30)),
        manager=manager
    )

# yes or no button
pedestrian_yes = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((600, 700), (50, 30)),
    text='Yes',
    manager=manager
)

pedestrian_no = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((660, 700), (50, 30)),
    text='No',
    manager=manager
)

selected_pedestrian = False

# Run simulation
run_simulation_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((900, 700), (150, 50)),
    text='Run Simulation',
    manager=manager
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

        screen.fill(WHITE)
        # draw text
        draw_title("Traffic flow rates", (20, 5))
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


        draw_font("Configurable parameters", (50, 600))

        # event handle
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            manager.process_events(event)

            # click on button event
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == pedestrian_yes:
                    selected_pedestrian = True
                elif event.ui_element == pedestrian_no:
                    selected_pedestrian = False

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

                    # initialise junction, ** is to unpack the dictionary and pass the key-value pair into class
                    junction = Junction(
                        **traffic_data,
                        #num_lanes=params["num_lanes"],
                        num_lanes = 0,
                        pedestrian_crossing = True,
                        simulation_duration = 0
                    )

                    print(junction)  # 打印实例化的 Junction 类数据

                    for key, box in traffic_flow_inputs.items():
                        box.kill()

                    for key, box in param_inputs.items():
                        box.kill()




                    game_state = 1

        # update gui, flip the screen
        manager.update(time_delta)
        manager.draw_ui(screen)
        pygame.display.flip()

    elif(game_state == 1):

        screen.fill(WHITE)

        manager.process_events(event)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False




        manager.update(time_delta)
        manager.draw_ui(screen)
        pygame.display.flip()

    elif (game_state == 2):
        pass


pygame.quit()