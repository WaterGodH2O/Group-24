from PIL import Image
import pygame

pygame.init()

# 读取GIF
gif = Image.open("example.gif")
frames = []
while True:
    frame = gif.convert("RGBA")
    pygame_frame = pygame.image.fromstring(frame.tobytes(), frame.size, "RGBA")
    frames.append(pygame_frame)
    try:
        gif.seek(gif.tell() + 1)
    except EOFError:
        break

# 创建窗口
screen = pygame.display.set_mode(gif.size)

# 动画循环
running = True
current_frame = 0
frame_delay = 100  # 毫秒
last_update = pygame.time.get_ticks()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    now = pygame.time.get_ticks()
    if now - last_update > frame_delay:
        current_frame = (current_frame + 1) % len(frames)
        last_update = now

    screen.blit(frames[current_frame], (0, 0))
    pygame.display.flip()

pygame.quit()