import sys
import subprocess
subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pygame'])
import pygame
import random
import time

fps = 30 
frame = (720, 480)

black = pygame.Color(0, 0, 0)
white = pygame.Color(255, 255, 255)
red = pygame.Color(255, 0, 0)
green = pygame.Color(0, 255, 0)
blue = pygame.Color(0, 0, 255)

fps_controller = pygame.time.Clock()

snake_speed = 5
snake_pos = [100, 50]
snake_body = [[100 - (i * 10), 50] for i in range(10)]
food_pos = [random.randrange(1, (frame[0]//10)) * 10,
            random.randrange(1, (frame[1]//10)) * 10]
food_spawn = True
direction = 'RIGHT'
score = 0
item_range = 10 #플레이어가 아이템을 먹을 수 있는 범위

magnet_radius_width = frame[0] * 1.2  # 초기 자기장 크기 화면 밖으로 설정
magnet_radius_height = frame[1] * 1.2 
magnet_decrease_rate = 5 #테스트용값
magnet_active = False
magnet_active_time = 2 #테스트용값
game_start_time = None
shrink_start_time = None
shrink_duration = 6  # 텍스트 UI 표시 시간 테스트용값

def Init(size):
    check_errors = pygame.init()
    if check_errors[1] > 0:
        print(f'[!] Had {check_errors[1]} errors when initialising game, exiting...')
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

def get_keyboard(cur_dir):
    keys = pygame.key.get_pressed()
    if direction != 'DOWN' and (keys[pygame.K_UP] or keys[ord('w')]):
        return 'UP'
    if direction != 'UP' and (keys[pygame.K_DOWN] or keys[ord('s')]):
        return 'DOWN'
    if direction != 'RIGHT' and (keys[pygame.K_LEFT] or keys[ord('a')]):
        return 'LEFT'
    if direction != 'LEFT' and (keys[pygame.K_RIGHT] or keys[ord('d')]):
        return 'RIGHT'
    return cur_dir

def update_magnet_radius(current_width, current_height, target_rect, decrease_rate):
    target_width = target_rect.width
    target_height = target_rect.height
    
    # 비율에 맞춰 축소
    width_ratio = (current_width - target_width) / current_width
    height_ratio = (current_height - target_height) / current_height
    
    # 비율에 맞춰 가로, 세로를 동시에 줄임
    current_width -= decrease_rate * width_ratio
    current_height -= decrease_rate * height_ratio
    
    return current_width, current_height

def draw_magnetic_field(window, current_width, current_height, target_rect):
    outer_surface = pygame.Surface((frame[0], frame[1]), pygame.SRCALPHA)
    outer_surface.fill((0, 0, 255, 50))

    inner_rect = pygame.Rect(
        target_rect.x + (target_rect.width - current_width) // 2,
        target_rect.y + (target_rect.height - current_height) // 2,
        current_width, current_height
    )

    pygame.draw.rect(outer_surface, (0, 0, 0, 0), inner_rect)

    window.blit(outer_surface, (0, 0))

    pygame.draw.rect(window, (0, 0, 255), inner_rect, 3)
    pygame.draw.rect(window, (255, 255, 255), target_rect, 2)

# 목표 영역 크기 설정
target_size_width = 500
target_size_height = 380
target_x = random.randint(50, frame[0] - target_size_width - 50)
target_y = random.randint(50, frame[1] - target_size_height - 50)
target_rect = pygame.Rect(target_x, target_y, target_size_width, target_size_height)

main_window = Init(frame)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    if game_start_time is None:
        game_start_time = time.time()

    if time.time() - game_start_time >= magnet_active_time:
        magnet_active = True
        if shrink_start_time is None:
            shrink_start_time = time.time()

    direction = get_keyboard(direction)

    if direction == 'UP':
        snake_pos[1] -= snake_speed
    if direction == 'DOWN':
        snake_pos[1] += snake_speed
    if direction == 'LEFT':
        snake_pos[0] -= snake_speed
    if direction == 'RIGHT':
        snake_pos[0] += snake_speed

    snake_body.insert(0, list(snake_pos))
    if abs(snake_pos[0] - food_pos[0]) < item_range and abs(snake_pos[1] - food_pos[1]) < item_range:
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

    if magnet_active:
        magnet_radius_width, magnet_radius_height = update_magnet_radius(magnet_radius_width, magnet_radius_height, target_rect, magnet_decrease_rate)

    main_window.fill(black)

    for pos in snake_body:
        pygame.draw.rect(main_window, green, pygame.Rect(pos[0], pos[1], 10, 10))

    pygame.draw.rect(main_window, white, pygame.Rect(food_pos[0], food_pos[1], 10, 10))

    draw_magnetic_field(main_window, magnet_radius_width, magnet_radius_height, target_rect)

    if snake_pos[0] < 0 or snake_pos[0] > frame[0] - 10 or snake_pos[1] < 0 or snake_pos[1] > frame[1] - 10:
        game_over(main_window, frame)

    for block in snake_body[1:]:
        if snake_pos[0] == block[0] and snake_pos[1] == block[1]:
            game_over(main_window, frame)

    show_score(main_window, frame, 1, white, 'consolas', 20)

    if magnet_active and shrink_start_time and time.time() - shrink_start_time <= shrink_duration:
        font = pygame.font.SysFont('times new roman', 25)
        text_surface = font.render("Magnetic Field is Shrinking!", True, white)
        main_window.blit(text_surface, (frame[0] // 2 - text_surface.get_width() // 2, 10))

    pygame.display.update()

    fps_controller.tick(fps)