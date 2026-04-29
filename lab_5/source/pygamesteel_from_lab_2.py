import pygame
import os

# Фикс для запуска в Docker без X-сервера (монитора)
os.environ['SDL_VIDEODRIVER'] = 'dummy'

pygame.init()

screen_width = 800
screen_height = 600
window_size = (screen_width, screen_height)
screen = pygame.display.set_mode(window_size) 

bg_color = (255, 255, 255)
font = pygame.font.SysFont(None, 75)
text = font.render("Hello appsec world*", True, (0, 255, 0))
text_rect = text.get_rect()
text_rect.center = (400, 300)

# Для Docker сделаем ограничение: выполним 100 итераций и выйдем
# Иначе контейнер будет крутиться вечно
running_count = 0
running = True
while running and running_count < 100:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(bg_color)
    screen.blit(text, text_rect)
    pygame.display.flip() 
    running_count += 1
    if running_count % 20 == 0:
        print(f"Frame {running_count} rendered successfully")

print("Pygame work finished successfully!")
pygame.quit()
