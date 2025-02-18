import sys
import subprocess
subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pygame'])
import pygame
import random
import time

fps = 15
frame = (720, 480)

black = pygame.Color(0, 0, 0)
white = pygame.Color(255, 255, 255)
red = pygame.Color(255, 0, 0)
green = pygame.Color(0, 255, 0)
blue = pygame.Color(0, 0, 255)

fps_controller = pygame.time.Clock()

snake_pos = [100, 50]
snake_body = [[100 - (i * 10), 50] for i in range(3)]
food_pos = [random.randrange(1, (frame[0]//10)) * 10,
            random.randrange(1, (frame[1]//10)) * 10]
food_spawn = True
direction = 'RIGHT'
score = 0

def Init(size):
    check_errors = pygame.init()
    if check_errors[1] > 0:
        print(
            f'[!] Had {check_errors[1]} errors when initialising game, exiting...')
        sys.exit(-1)
    else:
        print('[+] Game successfully initialised')
    pygame.display.set_caption('Snake Example with PyGame')
    game_window = pygame.display.set_mode(size)
    return game_window

def show_score(window, size, choice, color, font, fontsize):
    score_font = pygame.font.SysFont(font, fontsize)
    score_surface = score_font.render('Score : ' + str(score), True, color)
    score_rect = score_surface.get_rect()

    if choice == 1:
        score_rect.midtop = (size[0]/10, 15)
    else:
        score_rect.midtop = (size[0]/2, size[1]/1.25)

    window.blit(score_surface, score_rect)

def game_over(window, size):
    my_font = pygame.font.SysFont('times new roman', 90)
    game_over_surface = my_font.render('Game Over', True, red)
    game_over_rect = game_over_surface.get_rect()
    game_over_rect.midtop = (size[0]/2, size[1]/4)

    window.fill(black)
    window.blit(game_over_surface, game_over_rect)

    show_score(window, size, 0, green, 'times', 20)

    pygame.display.flip()

    time.sleep(3)
    pygame.quit()
    sys.exit()


def get_keyboard(key, cur_dir):
    if direction != 'DOWN' and key == pygame.K_UP or key == ord('w'):
        return 'UP'
    if direction != 'UP' and key == pygame.K_DOWN or key == ord('s'):
        return 'DOWN'
    if direction != 'RIGHT' and key == pygame.K_LEFT or key == ord('a'):
        return 'LEFT'
    if direction != 'LEFT' and key == pygame.K_RIGHT or key == ord('d'):
        return 'RIGHT'
    return cur_dir

main_window = Init(frame)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
            else:
                direction = get_keyboard(event.key, direction)

    if direction == 'UP':
        snake_pos[1] -= 10
    if direction == 'DOWN':
        snake_pos[1] += 10
    if direction == 'LEFT':
        snake_pos[0] -= 10
    if direction == 'RIGHT':
        snake_pos[0] += 10

    snake_body.insert(0, list(snake_pos))
    if snake_pos[0] == food_pos[0] and snake_pos[1] == food_pos[1]:
        score += 1
        food_spawn = False
    else:
        snake_body.pop()

    if not food_spawn:
        food_pos = [
            random.randrange(1, (frame[0]//10)) * 10,
            random.randrange(1, (frame[1]//10)) * 10
        ]
    food_spawn = True

    main_window.fill(black)
    for pos in snake_body:
        pygame.draw.rect(main_window, green,
                         pygame.Rect(pos[0], pos[1], 10, 10))

    pygame.draw.rect(main_window, white,
                     pygame.Rect(food_pos[0], food_pos[1], 10, 10))

    if snake_pos[0] < 0 or snake_pos[0] > frame[0] - 10:
        game_over(main_window, frame)
    if snake_pos[1] < 0 or snake_pos[1] > frame[1] - 10:
        game_over(main_window, frame)

    for block in snake_body[1:]:
        if snake_pos[0] == block[0] and snake_pos[1] == block[1]:
            game_over(main_window, frame)

    show_score(main_window, frame, 1, white, 'consolas', 20)

    pygame.display.update()

    fps_controller.tick(fps)