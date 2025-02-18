# %% [markdown]
# ### Pygame Example 진호정

# %% [markdown] #윤정환
# #### 0. 예제 설명(Introduction)
# Pygame은 쉽게 Game을 제작할 수 있도록 만들어진 module의 집합입니다. #정상현
# Pygame은 쉽게 Game을 제작할 수 있도록 만들어진 module의 집합입니다. <진재희>
# Python과 제공되는 간단한 몇가지의 함수만을 사용하여 실제로 구동할 수 있는 수준으로 만들 수 있습니다.
# 자세한 사항은 [Pygame Homepage](https://www.pygame.org/)를 참조해주세요.
#
# Pygame is a set of python module for writing game easliy.
# This allows you to create fully featured games and multimedia programs in the python language.
# You can see more details in [Pygame Homepage](https://www.pygame.org/).

# %% [markdown]
# ##### 0-1. 사전 준비(prerequirements)
# Pygame을 사용하기 위해 `pip`를 통한 pygame library를 설치합니다.
# 이 코드는 시작 후 한번만 실행해도 됩니다.
#
# You should install Pygame library with `pip` module
# This code only needs to be run once after startup.

# %%
# Jupyter 내부에서 shell command 실행을 위해 '%'를 사용하여 'pip'를 실행합니다.
# Insert `%` before running 'pip' command for running shell commands on Jupyter
# %pip install pygame

# %%
# Python으로 실행하고 싶으시다면 위 코드를 삭제하시고 아래의 코드를 실행해주세요.
# Delete the '%pip' code and run this code if you want to run on python
import os.path 
import logging
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

# %% [markdown]
# ##### 1-3. 기본 logic 함수 모음(basic logics of the game)
# 게임을 플레이하기 위해 필요한 함수들의 모음입니다.
# 자세한 부분은 각 주석을 확인해주세요.
#
# This is the set of functions that are required in the game.
# You can see more details in comments on each cell.


#최고기록 갱신코드
def refresh_record(score):
    logger = logging.getLogger()
    logger.info("score : {}".format(score))
    file = "record.txt"

    # 파일이 없으면 초기값 0
    if not os.path.isfile(file) or os.path.getsize(file) == 0:
        f = open(file, "w")
        f.write("0")
        f.close()

    # 파일 읽기 (최고 점수 확인)
    f = open(file, "r")
    record = int(f.read().strip())
    f.close()

    # 최고 기록 갱신 시에만 파일 쓰기
    if score > record:
        f = open(file, "w")
        f.write(str(score))
        f.close()
# %%
# Score
def show_highscore(window, size, color, font, fontsize):
    # Score를 띄우기 위한 설정입니다.
    # Settings for showing score on screen
    file = "record.txt"
    f = open(file, "r")
    record = int(f.read().strip())
    score_font = pygame.font.SysFont(font, fontsize)
    score_surface = score_font.render('High Score : ' + str(record), True, color)
    score_rect = score_surface.get_rect()

    # Game over 상황인지 게임중 상황인지에 따라 다른 위치를 선정합니다.
    # Select different location depending on the situation.

    score_rect.midtop = (size[0]/2, size[1]/1.15)#size[1]/1.25

    # 설정한 글자를 window에 복사합니다.
    # Copy the string to windows
    window.blit(score_surface, score_rect)

# %%
# Score
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

    refresh_record(score)
    # 'show_score' 함수를 부릅니다.
    # Call 'show_score' function.
    show_score(window, size, 0, green, 'times', 20)
    show_highscore(window, size, blue, 'times', 20)
    # 그려진 화면을 실제로 띄워줍니다.
    # Show drawn windows to screen
    pygame.display.flip()
    # 3초 기다린 후 게임을 종료합니다.
    # exit program after 3 seconds.
    time.sleep(3)
    pygame.quit()
    sys.exit()


# %%
# Keyboard input
def get_keyboard(key, cur_dir):
    # WASD, 방향키를 입력 받으면 해당 방향으로 이동합니다.
    # 방향이 반대방향이면 무시합니다.
    # Chnage direction using WASD or arrow key
    # Ignore keyboard input if input key has opposite direction
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