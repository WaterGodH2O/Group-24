import pygame

pygame.init()
screen = pygame.display.set_mode((1200, 800))
pygame.display.set_caption("事件处理示例")

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:  # 按键按下
            print(f"按下了 {event.key}")
        elif event.type == pygame.MOUSEBUTTONDOWN:  # 鼠标点击
            print(f"鼠标点击位置: {event.pos}")

pygame.quit()