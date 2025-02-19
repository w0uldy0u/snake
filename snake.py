import sys
import subprocess
subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pygame'])
import pygame
import random
import time
import logging
import os
record = 0
fpscnt = 0
fps = 60
frame = (720, 630)
game_frame = (720, 480)

black = pygame.Color(0, 0, 0)
white = pygame.Color(255, 255, 255)
red = pygame.Color(255, 0, 0)
green = pygame.Color(0, 255, 0)
blue = pygame.Color(0, 0, 255)
yellow = pygame.Color(255, 255, 0)
fps_controller = pygame.time.Clock()

snake_speed = 3
snake_acc = 0.01
snake_pos = [100, 50]
snake_body = [[100 - (i * 10), 50] for i in range(10)]

food_pos = [random.randrange(1, (game_frame[0]//10)) * 10,
            random.randrange(1, (game_frame[1]//10)) * 10]
double_score_item_pos = [0,0]
food_spawn = True
food_gen_count = 0
inittime = time.time()
food_positions = [{"pos":[random.randrange(1, (game_frame[0] // 10)) * 10, random.randrange(1, (game_frame[1] // 10)) * 10  ],"color": white, "size": (20, 20), "effect": "score_3","time":inittime},
                  {"pos":[random.randrange(1, (game_frame[0] // 10)) * 10,random.randrange(1, (game_frame[1] // 10)) * 10 ],"color": white, "size": (10, 10), "effect": "score_5","time":inittime},
                  {"pos":[random.randrange(1, (game_frame[0] // 10)) * 10,random.randrange(1, (game_frame[1] // 10)) * 10  ],"color": white, "size": (30, 30), "effect": "score_1","time":inittime}]

direction = 'RIGHT'

# 일시정지 상태 변수
paused = False

health = 10
score = 0
item_range = 10 #플레이어가 아이템을 먹을 수 있는 범위

double_score_active = False
double_score_start_time = None
double_score_duration = 8 #테스트용값


magnet_radius_width = game_frame[0] * 1.2  # 초기 자기장 크기 화면 밖으로 설정
magnet_radius_height = game_frame[1] * 1.2 
magnet_decrease_rate = 3 #테스트용값
magnet_active = False
magnet_active_time = 10 #테스트용값
game_start_time = None
shrink_start_time = None
shrink_duration = 5  # 텍스트 UI 표시 시간 테스트용값
food_spawn_probability = 0.7 # 음식 자기장 안 생성 확률 테스트용값***
safe_time = 0.5 # 자기장 밖에서 체력 닳는 주기 테스트용값**

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
def get_record():
    file = "record.txt"
    if not os.path.isfile(file) or os.path.getsize(file) == 0:
        return 0
    f = open(file, "r")
    record = int(f.read().strip())
    f.close()
    return record
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
        return score
    return record
def show_highscore(window, size, choice, color, font, fontsize):
    score_font = pygame.font.SysFont(font, fontsize)
    score_surface = score_font.render('High Score : ' + str(record), True, color)
    score_rect = score_surface.get_rect()

    if choice == 1:
        score_rect.midleft = (10, size[1]/1.15)
    else:
        score_rect.midtop = (size[0]/2, size[1]/1.15)

    window.blit(score_surface, score_rect)

def show_score(window, size, choice, color, font, fontsize):
    score_font = pygame.font.SysFont(font, fontsize)
    score_surface = score_font.render('Score : ' + str(score), True, color)
    score_rect = score_surface.get_rect()

    if choice == 1:
        score_rect.midleft = (10, size[1]/1.2)
    else:
        score_rect.midtop = (size[0]/2, size[1]/1.25)

    window.blit(score_surface, score_rect)

def game_over(window, size):
    global score, health, snake_pos, snake_body, food_positions, direction, food_gen_count, double_score_active, double_score_start_time, magnet_active, magnet_radius_width, magnet_radius_height, shrink_start_time, last_damage_time

    my_font = pygame.font.SysFont('times new roman', 90)
    game_over_surface = my_font.render('Game Over', True, red)
    game_over_rect = game_over_surface.get_rect()
    game_over_rect.midtop = (size[0]/2, size[1]/4)

    window.fill(black)
    window.blit(game_over_surface, game_over_rect)

    # 최고 점수 갱신
    record = refresh_record(score)
    show_score(window, size, 0, white, 'times', 20)
    show_highscore(window, size,0, green, 'times', 20)

    # 재시작/종료 선택지
    font = pygame.font.SysFont('times new roman', 30)
    restart_text = font.render("Press R to Restart or Q to Quit", True, white)
    restart_rect = restart_text.get_rect()
    restart_rect.midtop = (size[0]/2, size[1]/1.5)
    window.blit(restart_text, restart_rect)
    
    pygame.display.flip()

    waiting_for_input = True
    while waiting_for_input:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r: 
                    restart_game()
                    waiting_for_input = False
                elif event.key == pygame.K_q: 
                    pygame.quit()
                    sys.exit()

#게임 상태 초기화 함수
def restart_game():
    global score, health, snake_pos, snake_body, food_positions, direction, food_gen_count, double_score_active, double_score_start_time, magnet_active, magnet_radius_width, magnet_radius_height, shrink_start_time, last_damage_time
    
    score = 0
    health = 10
    snake_pos = [100, 50]
    snake_body = [[100 - (i * 10), 50] for i in range(10)]
    food_positions = []
    food_gen_count = 0
    direction = 'RIGHT'
    double_score_active = False
    double_score_start_time = None
    magnet_active = False
    magnet_radius_width = game_frame[0] * 1.2
    magnet_radius_height = game_frame[1] * 1.2
    shrink_start_time = None
    last_damage_time = time.time()

    global game_start_time
    game_start_time = None

def toggle_pause():
    global paused
    paused = not paused

# 일시정지 화면 표출 함수
def pause_screen(window,size):
    pause_font = pygame.font.SysFont('times new roman', 50)
    pause_surface = pause_font.render('PAUSED', True, red)
    pause_rect = pause_surface.get_rect()
    pause_rect.midtop = (size[0] / 2, size[1] / 3)
    window.fill(black)
    window.blit(pause_surface, pause_rect)

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

def generate_food():
    global food_positions
    created_time = time.time() # 현재 시간
    # 일정 확률로 자기장 안에 음식을 생성
    if random.random() < food_spawn_probability:
        food_x = random.randint(target_rect.x, target_rect.x + target_rect.width - 10)
        food_y = random.randint(target_rect.y, target_rect.y + target_rect.height - 10)
        item_type = random.choice(["confuse", "double_score", "hp_up", "hp_down", "score_3", "score_5", "score_1"])
        x = food_x // 10 * 10
        y = food_y // 10 * 10
        if item_type == "confuse":
            food_positions.append({"pos": [x, y], "color": green, "size": (10, 10), "effect": "confuse","time":created_time})
        elif item_type == "double_score":
            food_positions.append({"pos": [x, y], "color": blue, "size": (10, 10), "effect": "double_score","time":created_time})
        elif item_type == "hp_up":
            food_positions.append({"pos": [x, y], "color": red, "size": (10, 10), "effect": "hp_up","time":created_time})
        elif item_type == "hp_down":
            food_positions.append({"pos": [x, y], "color": yellow, "size": (10, 10), "effect": "hp_down","time":created_time})
        elif item_type == "score_3":
            food_positions.append({"pos": [x, y], "color": white, "size": (20, 20), "effect": "score_3","time":created_time})  # 2×2 크기
        elif item_type == "score_5":
            food_positions.append({"pos": [x, y], "color": white, "size": (10, 10), "effect": "score_5","time":created_time})  # 1×1 크기
        elif item_type == "score_1":
            food_positions.append({"pos": [x, y], "color": white, "size": (30, 30), "effect": "score_1","time":created_time})  # 3×3 크기
        #food_positions.append({"pos":[food_x // 10 * 10, food_y // 10 * 10], "color":})
    else:
        # 나머지 확률로 화면 내 임의의 위치 생성
        x = random.randrange(1, (game_frame[0] // 10)) * 10
        y = random.randrange(1, (game_frame[1] // 10)) * 10
        item_type = random.choice(["confuse", "double_score", "hp_up", "hp_down", "score_3", "score_5", "score_1"])
        if item_type == "confuse":
            food_positions.append({"pos": [x, y], "color": green, "size": (10, 10), "effect": "confuse","time":created_time})
        elif item_type == "double_score":
            food_positions.append({"pos": [x, y], "color": blue, "size": (10, 10), "effect": "double_score","time":created_time})
        elif item_type == "hp_up":
            food_positions.append({"pos": [x, y], "color": red, "size": (10, 10), "effect": "hp_up","time":created_time})
        elif item_type == "hp_down":
            food_positions.append({"pos": [x, y], "color": yellow, "size": (10, 10), "effect": "hp_down","time":created_time})
        elif item_type == "score_3":
            food_positions.append({"pos": [x, y], "color": white, "size": (20, 20), "effect": "score_3","time":created_time})  # 2×2 크기
        elif item_type == "score_5":
            food_positions.append({"pos": [x, y], "color": white, "size": (10, 10), "effect": "score_5","time":created_time})  # 1×1 크기
        elif item_type == "score_1":
            food_positions.append({"pos": [x, y], "color": white, "size": (30, 30), "effect": "score_1","time":created_time})  # 3×3 크기
    print("food_pos : ",food_positions)
    return food_positions

def apply_item_effect(effect):
    global score, health,double_score_active, double_score_start_time
    if effect == "confuse":
        # 함수 추가
        print("confuse")
    
    elif effect == "double_score":
        #함수 추가
        print("double_score")
        double_score_active = True
        double_score_start_time = time.time()
    
    elif effect == "hp_up":
        print("hp_up")
        health = min(10, health + 2)  # 최대 HP 제한
    
    elif effect == "hp_down":
        print("hp_down")
        health = max(0, health - 2)  # 최소 HP 제한
    
    elif effect == "score_3":
        print("score_3")
        if double_score_active:
            score += 6
        else:
            score += 3
    
    elif effect == "score_5":
        print("score_5")
        if double_score_active:
            score += 10
        else:
            score += 5
    
    elif effect == "score_1":
        print("score_1")
        if double_score_active:
            score += 2
        else:
            score += 1
def remove_expired_items():
    global food_positions, food_gen_count
    current_time = time.time()
    for food in food_positions:
        if current_time - food["time"] >= 5:
            food_positions.remove(food)
            food_gen_count += 1
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
    outer_surface = pygame.Surface((frame[0], game_frame[1]), pygame.SRCALPHA)  # UI 제외
    if magnet_active:
        outer_surface.fill((0, 0, 255, 50))

    inner_rect = pygame.Rect(
        target_rect.x + (target_rect.width - current_width) // 2,
        target_rect.y + (target_rect.height - current_height) // 2,
        current_width, min(current_height, game_frame[1])  # UI 영역에 안 겹치게 제한
    )

    pygame.draw.rect(outer_surface, (0, 0, 0, 0), inner_rect)
    window.blit(outer_surface, (0, 0))
    if magnet_active:
        pygame.draw.rect(window, (0, 0, 255), inner_rect, 3)
    pygame.draw.rect(window, (255, 255, 255), target_rect, 2)


def draw_health_bar(window):
    global health
    health_text = pygame.font.SysFont('consolas', 20).render('HEALTH : ', True, white)
    window.blit(health_text, (10, 491))

    for i in range(10):
        x_pos = 10 + (i * 30) + health_text.get_width() + 5 
        y_pos = 491
        if i < health:
            pygame.draw.rect(window, red, pygame.Rect(x_pos, y_pos, 20, 20))
        else:
            pygame.draw.rect(window, white, pygame.Rect(x_pos, y_pos, 20, 20))

#체력 실시간 업데이트
def update_health():
    global health
    check_outside_magnet()

    if health <= 0:
        game_over(main_window, frame)

def check_outside_magnet():
    global health, last_damage_time

    inner_rect = pygame.Rect(
        target_rect.x + (target_rect.width - magnet_radius_width) // 2,
        target_rect.y + (target_rect.height - magnet_radius_height) // 2,
        magnet_radius_width, magnet_radius_height
    )

    if not inner_rect.collidepoint(snake_pos):
        current_time = time.time()
        
        if current_time - last_damage_time >= safe_time:
            health -= 1
            last_damage_time = current_time

def check_double_score_item_collision():
    global double_score_active, double_score_start_time
    # 점수 2배 아이템 충돌 검사
    if abs(snake_pos[0] - double_score_item_pos[0]) < item_range and abs(snake_pos[1] - double_score_item_pos[1]) < item_range:
        double_score_active = True
        double_score_start_time = time.time()
        return True
    return 

def update_double_score_effect():
    global double_score_active, double_score_start_time
    # 2배 효과 시간이 끝났으면 비활성화
    if double_score_active and time.time() - double_score_start_time >= double_score_duration:
        double_score_active = False

# def draw_snake():
#     for i, segment in enumerate(snake_body[1:]):
#         x, y = segment[0], segment[1]
#         # 뱀 몸통 그리기
#         green_intensity = 255 - (i * 10)  # 뱀의 색상 그라디언트 효과
#         pygame.draw.rect(main_window, (green_intensity, 255, 0), pygame.Rect(x, y, 10, 10))


# 목표 영역 크기 설정
target_size_width = 500
target_size_height = 380
target_x = random.randint(50, game_frame[0] - target_size_width - 50)
target_y = random.randint(50, game_frame[1] - target_size_height - 50)
target_rect = pygame.Rect(target_x, target_y, target_size_width, target_size_height)

main_window = Init(frame)
last_damage_time = time.time()

record = get_record()
while True:
    remove_expired_items()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:  # ESC로 종료
                pygame.event.post(pygame.event.Event(pygame.QUIT))
            elif event.key == ord('p'):  # p 키를 눌러 일시정지
                toggle_pause()
            else:
                if not paused:
                    direction = get_keyboard(event.key, direction)

    if game_start_time is None:
        game_start_time = time.time()

    if time.time() - game_start_time >= magnet_active_time:
        magnet_active = True
        if shrink_start_time is None:
            shrink_start_time = time.time()

    if paused:
        pause_screen(main_window,frame)
        pygame.display.update()
        continue

    if direction == 'UP':
        snake_pos[1] -= snake_speed
    if direction == 'DOWN':
        snake_pos[1] += snake_speed
    if direction == 'LEFT':
        snake_pos[0] -= snake_speed
    if direction == 'RIGHT':
        snake_pos[0] += snake_speed

    snake_body.insert(0, list(snake_pos))
    # 고쳐야되는 부분{
    flag = -1
    '''
    for i in range(len(food_positions)):
        if abs(snake_pos[0] - food_positions[i][0]) < item_range and abs(snake_pos[1] - food_positions[i][1]) < item_range:
            score += 1
            food_positions.pop(i)
            food_gen_count +=1
            flag = 1
    #만약 음식을 먹지 않았다면
    '''
    for food in food_positions:
        if abs(snake_pos[0] - food["pos"][0]) < food["size"][0] and abs(snake_pos[1] - food["pos"][1]) < food["size"][0]:
            apply_item_effect(food["effect"])
            food_positions.remove(food)
            food_gen_count += 1
            flag = 1
    if flag == -1:
        snake_body.pop()
    #호정님 코드
    #check_double_score_item_collision()
    if double_score_active:
        update_double_score_effect()
        
    #호정님 코드

    if food_gen_count >=1:
        food_gen_count -=1
        generate_food()

    # if not food_spawn:
    #    food_pos = generate_food()
    #food_spawn = True
    #}
    if magnet_active:
        magnet_radius_width, magnet_radius_height = update_magnet_radius(magnet_radius_width, magnet_radius_height, target_rect, magnet_decrease_rate)

    main_window.fill(black)
    # draw_snake()
    for pos in snake_body:
        pygame.draw.rect(main_window, green, pygame.Rect(pos[0], pos[1], 10, 10))
    '''
        for food in food_positions:
        if abs(snake_pos[0] - food["pos"][0]) < item_range and abs(snake_pos[1] - food["pos"][1]) < item_range:
            apply_item_effect(food["effect"])
            food_positions.remove(food)
            food_gen_count += 1
            flag = 1
        '''
    #for i in range(len(food_positions)):
    #    pygame.draw.rect(main_window, white, pygame.Rect(food_positions[i][0], food_positions[i][1], 10, 10))
    for food in food_positions:
        pygame.draw.rect(main_window, food["color"], pygame.Rect(food["pos"][0], food["pos"][1], food["size"][0], food["size"][1]))


    update_health()
    pygame.draw.line(main_window, white, (0, 480), (frame[0], 480), 5)


    draw_magnetic_field(main_window, magnet_radius_width, magnet_radius_height, target_rect)

    if snake_pos[0] < 0 or snake_pos[0] > game_frame[0] - 10 or snake_pos[1] < 0 or snake_pos[1] > game_frame[1] - 10:
        game_over(main_window, frame)

    for block in snake_body[1:]:
        if snake_pos[0] == block[0] and snake_pos[1] == block[1]:
            game_over(main_window, frame)

    show_score(main_window, frame, 1, white, 'consolas', 20)
    show_highscore(main_window, frame ,1, green, 'consolas', 20)
    draw_health_bar(main_window)

    if magnet_active and shrink_start_time and time.time() - shrink_start_time <= shrink_duration:
        font = pygame.font.SysFont('times new roman', 25)
        text_surface = font.render("Magnetic Field is Shrinking!", True, white)
        main_window.blit(text_surface, (frame[0] // 2 - text_surface.get_width() // 2, 10))
    
    pygame.display.update()

    fps_controller.tick(fps)
    fpscnt += 1
    if fpscnt>=150:
        fpscnt = 0
        snake_speed += snake_acc