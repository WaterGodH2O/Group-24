import pygame
import pygame_gui

pygame.init()

# 设置窗口
pygame.display.set_caption('Delete UI Element Example')
window_size = (800, 600)
screen = pygame.display.set_mode(window_size)

# 创建背景
background = pygame.Surface(window_size)
background.fill(pygame.Color('#000000'))

# 创建 UI 管理器
manager = pygame_gui.UIManager(window_size)

# 创建一个按钮
button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((350, 275), (100, 50)),
    text='Click Me',
    manager=manager
)

# 创建一个删除按钮
delete_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((350, 350), (100, 50)),
    text='Delete Button',
    manager=manager
)

clock = pygame.time.Clock()
running = True

while running:
    time_delta = clock.tick(60) / 1000.0  # 60 FPS

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        manager.process_events(event)

        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == button:
                    print("Main Button Clicked!")
                elif event.ui_element == delete_button:
                    print("Delete Button Clicked! Deleting main button.")
                    button.kill()  # 删除 main button

    manager.update(time_delta)

    screen.blit(background, (0, 0))
    manager.draw_ui(screen)

    pygame.display.update()

pygame.quit()
