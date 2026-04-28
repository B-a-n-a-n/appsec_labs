import pygame
pygame.init()

# Устанавливаем размеры окна
screen_width = 800
screen_height = 600
window_size = (screen_width, screen_height)
# добавили переменную 'screen'
screen = pygame.display.set_mode(window_size) 

# Задаем цвет фона
bg_color = (255, 255, 255)

# Подготовка текста
font = pygame.font.SysFont(None, 75)
text = font.render("Hello appsec world*", True, (0, 255, 0))
text_rect = text.get_rect()
text_rect.center = (400, 300)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # отрисовка фона и обновление экрана перенесены в цикл 
    screen.fill(bg_color) # Очищаем экран белым цветом
    screen.blit(text, text_rect) # Рисуем текст
    pygame.display.flip() 

pygame.quit()
