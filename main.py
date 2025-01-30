import pygame
import pygame_gui


from Junction import Junction

game_state:int = 0


# 初始化 pygame
pygame.init()

# 窗口大小
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Traffic Junction Simulation")

# 创建 GUI 管理器
manager = pygame_gui.UIManager((WIDTH, HEIGHT))

# 颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# 字体

title = pygame.font.Font(None, 35)  # 仅传入字体和大小
title.set_bold(True)                # 启用加粗
title.set_italic(True)

font = pygame.font.Font(None, 29)

def draw_title(text, position):
    text_surface = title.render(text, True, BLACK, )
    screen.blit(text_surface, position)


def draw_font(text, position):
    text_surface = font.render(text, True, BLACK)
    screen.blit(text_surface, position)


# 交通流量输入框坐标
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

# 配置参数输入框坐标
param_positions = {
    "num_lanes": (400, 650),
    "crossing_time": (650, 650),
    "crossing_frequency": (900, 650),
    "simulation_duration": (400, 700),
}

# 交通流量输入框
traffic_flow_inputs = {}
for key, pos in traffic_flow_positions.items():
    Rectangle = pygame.Rect(pos, (80, 30))

    traffic_flow_inputs[key] = pygame_gui.elements.UITextEntryLine(relative_rect=Rectangle, manager=manager)

# 配置参数输入框
param_inputs = {}
for key, pos in param_positions.items():
    Rectangle = pygame.Rect(pos, (80, 30))
    param_inputs[key] = pygame_gui.elements.UITextEntryLine(
        relative_rect=pygame.Rect(pos, (80, 30)),
        manager=manager
    )

# 手动实现 Yes/No 单选按钮
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

selected_pedestrian = False  # 默认无行人过道

# 运行仿真按钮
run_simulation_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((900, 700), (150, 50)),
    text='Run Simulation',
    manager=manager
)

# 游戏状态
game_state = 0
clock = pygame.time.Clock()
running = True

while running:
    # set the simulation FPS as 60
    # this function will return the time interval between this frame and previous frame in ms
    # it should be 16.67 ms (60 frame per second) if not lag
    # ----um my cursor flashing in 60fps so I just changed it to 240, dont mind it
    time_delta = clock.tick(240)


    screen.fill(WHITE)

    # 绘制标签
    draw_title("Traffic flow rates", (20, 20))
    draw_font("North", (50, 115))

    draw_font("Exiting North", (550, 150))
    draw_font("Exiting East", (650, 150))
    draw_font("Exiting South", (750, 150))
    draw_font("Exiting West", (850, 150))
    draw_font("Configurable parameters", (50, 600))

    # 事件处理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        manager.process_events(event)

        # 按钮点击事件
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == pedestrian_yes:
                    selected_pedestrian = True
                elif event.ui_element == pedestrian_no:
                    selected_pedestrian = False
                elif event.ui_element == run_simulation_button:
                    # 获取所有输入值
                    traffic_data = {}
                    for key, input_box in traffic_flow_inputs.items():
                        traffic_data[key] = int(input_box.get_text() or 0)

                    params = {}
                    for key, input_box in param_inputs.items():
                        params[key] = int(input_box.get_text() or 0)

                    # 实例化 Junction 类
                    junction = Junction(
                        **traffic_data,
                        num_lanes=params["num_lanes"],
                        pedestrian_crossing=selected_pedestrian,
                        crossing_time=params["crossing_time"],
                        crossing_frequency=params["crossing_frequency"],
                        simulation_duration=params["simulation_duration"]
                    )

                    print(junction)  # 打印实例化的 Junction 类数据

    # 更新 GUI
    manager.update(time_delta)
    manager.draw_ui(screen)
    pygame.display.flip()

pygame.quit()