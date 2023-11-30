import random,math
import sys
import data.entities as e
import data.lines as line_math
import data.text as text
from data.button import Button
from data.core_funcs import *
from pygame.locals import *

# Setup pygame/cửa sổ game --------------------------------------------------------------------------------------------#
mainClock = pygame.time.Clock()

BORDER_WIDTH = 100
BG = pygame.image.load("data/images/Background2.png")
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.mixer.set_num_channels(32)
pygame.display.set_caption('Lyneste')
screen = pygame.display.set_mode((550 + 2 * BORDER_WIDTH, 800), 0, 32)
ico = pygame.image.load('data/images/ico.png')
pygame.display.set_icon(ico)
display = pygame.Surface((275, 400))
gui_display = pygame.Surface((275, 400))
gui_display.set_colorkey((0, 0, 0))

e.load_particle_images('data/images/particles')
e.set_global_colorkey((0, 0, 0))

# lấy phông chữ qua hàm Font (text.py) --------------------------------------------------------------------------------#
font = text.Font('data/fonts/large_font.png', (255, 255, 255))
font2 = text.Font('data/fonts/large_font.png', (0, 0, 1))


def get_font(size):  # Returns Press-Start-2P in the desired size
    return pygame.font.Font("data/fonts/font.ttf", size)


# khởi tạo sound effect và nhạc nền -----------------------------------------------------------------------------------#

bounce_s = pygame.mixer.Sound('data/sfx/bounce.wav')  # nảy
death_s = pygame.mixer.Sound('data/sfx/death.wav')  # thua
click_s = pygame.mixer.Sound('data/sfx/click.wav')  # đặt điểm
restart_s = pygame.mixer.Sound('data/sfx/restart.wav')  # chơi lại
closing_s = pygame.mixer.Sound('data/sfx/closing.mp3')  # thoát


# Background music controller -----------------------------------------------------------------------------------------#
def bgmc(x):
    pygame.mixer.music.unload()
    if x == 0:
        pygame.mixer.music.load('data/sfx/Stellar.wav')
    elif x == 1:
        pygame.mixer.music.load('data/sfx/ingame.mp3')
    else:
        pygame.mixer.music.load('data/sfx/suisex.mp3')
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(loops=-1, start=0.0, fade_ms=750)


# chỉnh âm lượng ------------------------------------------------------------------------------------------------------#
bounce_s.set_volume(0.7)
click_s.set_volume(0.9)
restart_s.set_volume(0.7)

# định nghĩa màu ------------------------------------------------------------------------------------------------------#
background_color = (13, 20, 33)  # nền
background_polygon_color = (24, 34, 46)  # hiệu ứng
line_color = (255, 255, 255)  # đường kẻ
line_placing_color = (90, 140, 170)  # preview đường kẻ
line_width = 3  # độ dày đường kẻ


# kiểm tra hướng bóng hiện tại so với đường kẻ khi va chạm -------------------------------------------------------------#
def check_line_sides(lines, point):
    line_status = []
    for line in lines:
        line_status.append(
            (line[1][0] - line[0][0]) * (point[1] - line[0][1]) - (line[1][1] - line[0][1]) * (point[0] - line[0][0]))
    return line_status


# kiểm tra âm ----------------------------------------------------------------------------------------------------------#
def sign(num):
    if num != 0:
        return num / abs(num)
    else:
        return 1


# tính góc nảy ---------------------------------------------------------------------------------------------------------#
def mirror_angle(original, base):
    dif = 180 - base
    base = 180
    new = original + dif
    new = new % 360
    dif = base - new
    return original + dif * 2


# tính khoảng cách giữa 2 điểm ----------------------------------------------------------------------------------------#
def dis_func(dis):
    return math.sqrt(dis[0] ** 2 + dis[1] ** 2)


def redrawWindow():
    screen.blit(BG, (0, 0))


# fade effect ---------------------------------------------------------------------------------------------------------#
def fade():
    fade = pygame.Surface((550 + 2 * BORDER_WIDTH, 800))
    fade.fill((0, 0, 0))
    pygame.mixer.music.fadeout(1400)
    for alpha in range(150, 300):
        fade.set_alpha(alpha)
        redrawWindow()
        screen.blit(fade, (0, 0))
        pygame.display.update()


def pause():
    paused = True
    while paused:
        pygame.event.set_grab(False)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == K_SPACE:
                    paused = False
                elif event.key == K_m:
                    click_s.play()
                    main_menu()
        screen.fill(background_color)
        pauset = get_font(80).render("Paused", True, "#ffffff")
        button_rect = pauset.get_rect(center=(375, 400))
        screen.blit(pauset, button_rect)
        pygame.display.update()


# Main menu ------------------------------------------------------------------------------------------------------------#
def main_menu():
    bgmc(0)
    while True:
        BG = pygame.image.load("data/images/Background2.png")
        screen.blit(BG, (0, 0))
        mp = pygame.mouse.get_pos()

        title = get_font(80).render("LYNESTE", True, "#b68f40")
        button_rect = title.get_rect(center=(375, 200))

        PLAY_BUTTON = Button(image=pygame.image.load("data/images/Play Rect.png"), pos=(380, 450),
                             text_input="PLAY", font=get_font(50), base_color="#d7fcd4", hovering_color="Yellow")
        QUIT_BUTTON = Button(image=pygame.image.load("data/images/Quit Rect.png"), pos=(380, 600),
                             text_input="QUIT", font=get_font(50), base_color="#d7fcd4", hovering_color="Yellow")

        screen.blit(title, button_rect)

        for button in [PLAY_BUTTON, QUIT_BUTTON]:
            button.changeColor(mp)
            button.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click_s.play()
                    if PLAY_BUTTON.checkForInput(mp):
                        restart_s.play()
                        fade()
                        game()
                    if QUIT_BUTTON.checkForInput(mp):
                        closing_s.play()
                        fade()
                        pygame.quit()
                        sys.exit()

        pygame.display.update()


# Gamplay Loop ------------------------------------------------------------------------------------------------------- #
def game():
    # khởi tạo sân chơi -----------------------------------------------------------------------------------------------#
    bgmc(1)
    particles = []  # tập hiệu ứng
    platforms = [[[0, display.get_height() - 1], [display.get_width(), display.get_height() - 1]]]  # khung trò chơi
    last_point = [display.get_width() // 2, display.get_height()]  # khởi tạo điểm bắt đầu và điểm cuối nhấn trỏ
    scroll = 0  # khởi tạo giá trị lăn màn hình
    sparks = []
    circle_effects = []
    player_path = []
    game_score = 0
    end_game = False
    game_text_loc = -120
    end_text_loc = -220
    last_place = 50
    screen_shake = 0
    transition = 30

    # khởi tạo bóng----------------------------------------------------------------------------------------------------#
    player_pos = [display.get_width() // 2, display.get_height() // 2]  # vị trí đầu
    player_velocity = [0, 0]  # tốc độ di chuyển trên x y
    player_color = (90, 210, 255)  # màu
    bounce_cooldown = 0
    while True:
        pygame.event.set_grab(True)
        # Background --------------------------------------------- #
        if transition > 0:
            transition -= 1

        if screen_shake > 0:
            screen_shake -= 1

        if not end_game:
            line_color = (255, 255, 255)
            if player_pos[1] - 200 < scroll:
                scroll += (player_pos[1] - 200 - scroll) / 10
        else:
            line_color = (190, 197, 208)

        if (-scroll) - last_place > 50:
            if random.randint(1, 3) <= 2:
                base_y = scroll - 80
                base_x = random.randint(0, display.get_width())
                new_line = [[base_x, base_y],
                            [base_x + random.randint(0, 200) - 100, base_y + random.randint(0, 100) - 50]]
                if dis_func((new_line[1][0] - new_line[0][0], new_line[1][1] - new_line[0][1])) > 30:
                    new_line.sort()
                    platforms.append(new_line)
            last_place += 50

        game_score = max(game_score, -(player_pos[1] - display.get_height() // 2))

        display.fill(background_color)
        gui_display.fill((0, 0, 0))

        mx, my = pygame.mouse.get_pos()
        mx -= BORDER_WIDTH
        mx = mx // 2
        my = my // 2

        player_gravity = 0.05 + game_score / 30000
        player_terminal_velocity = 1 + game_score / 3000
        bounce_strength = 1 + game_score / 8000

        if end_game:
            scroll += (- scroll) / 100

        # Hiệu ứng chết ----------------------------------------- #
        for i, circle in sorted(enumerate(circle_effects),
                                reverse=True):  # loc, radius, border_stats, speed_stats, color
            circle[1] += circle[3][0]
            circle[2][0] -= circle[2][1]
            circle[3][0] -= circle[3][1]
            if circle[2][0] < 1:
                circle_effects.pop(i)
            else:
                pygame.draw.circle(display, circle[4], [int(circle[0][0]), int(circle[0][1] - scroll)], int(circle[1]),
                                   int(circle[2][0]))

        # kẻ đường preview ------------------------------------ #
        if not end_game:
            pygame.draw.line(display, line_placing_color, [last_point[0], last_point[1] - scroll], [mx, my])

        player_path = player_path[-50:]
        if len(player_path) > 2:
            player_path_mod = [[v[0], v[1] - scroll] for v in player_path]
            pygame.draw.lines(display, line_placing_color, False, player_path_mod)

        # kẻ đường -------------------------------------------- #
        for platform in platforms:
            if (min(platform[0][1], platform[1][1]) < scroll + display.get_height() + 20) and (
                    max(platform[0][1], platform[1][1]) > scroll - 20):
                pygame.draw.line(display, line_color, [platform[0][0], platform[0][1] - scroll],
                                 [platform[1][0], platform[1][1] - scroll], line_width)
                pygame.draw.circle(display, line_color, [platform[0][0], platform[0][1] - scroll], 6, 2)
                pygame.draw.circle(display, line_color, [platform[1][0], platform[1][1] - scroll], 6, 2)
                if random.randint(0, 10) == 0:
                    color = random.randint(150, 220)
                    sparks.append([random.choice(platform), random.randint(0, 359), random.randint(7, 10) / 10,
                                   5 * random.randint(5, 10) / 10, (color, color, color)])

        # Render Bóng --------------------------------------------------#
        particles.append(
            e.particle(player_pos, 'p', [random.randint(0, 20) / 40 - 0.25, random.randint(0, 10) / 15 - 1], 0.2,
                       random.randint(0, 30) / 10, player_color))
        for i, particle in sorted(enumerate(particles), reverse=True):
            alive = particle.update(1)
            if not alive:
                particles.pop(i)
            else:
                particle.draw(display, [0, scroll])

        line_locations = check_line_sides(platforms, player_pos)

        start_pos = player_pos.copy()
        # Tính tốc độ bóng ----------------------------------------------#
        player_velocity[1] = min(player_terminal_velocity, player_velocity[1] + player_gravity)
        player_pos[0] += player_velocity[0]
        player_pos[1] += player_velocity[1]
        player_velocity[1] = normalize(player_velocity[1], 0.02)

        player_path.append(player_pos.copy())

        if bounce_cooldown > 0:
            bounce_cooldown -= 1
        # Tính nảy bóng ------------------------------------------------#
        line_locations_post = check_line_sides(platforms, player_pos)
        for i, side in enumerate(line_locations):
            if sign(side) != sign(line_locations_post[i]):
                if sign(side) == -1:
                    if line_math.doIntersect([start_pos, player_pos], platforms[i]):
                        if (player_pos[0] < display.get_width()) and (player_pos[0] > 0):
                            if bounce_cooldown == 0:
                                bounce_s.play()
                                angle = math.atan2(platforms[i][1][1] - platforms[i][0][1],
                                                   platforms[i][1][0] - platforms[i][0][0])
                                normal = angle - math.pi * 0.5
                                bounce_angle = math.radians(
                                    mirror_angle(math.degrees(math.atan2(-player_velocity[1], -player_velocity[0])),
                                                 math.degrees(normal)) % 360)
                                player_velocity[0] = math.cos(bounce_angle) * (dis_func(player_velocity) + 1)
                                player_velocity[1] = math.sin(bounce_angle) * (dis_func(player_velocity) + 1)
                                player_velocity[1] -= 2 * bounce_strength
                                for i in range(random.randint(4, 6)):
                                    spark_angle = math.degrees(normal) + random.randint(0, 180) - 90
                                    sparks.append([player_pos.copy(), spark_angle,
                                                   (dis_func(player_velocity) + 1) / 3 * random.randint(7, 10) / 10,
                                                   (dis_func(player_velocity) + 1) * 2 * random.randint(5, 10) / 10])
                                bounce_cooldown = 3

        if (player_pos[0] < 0) or (player_pos[0] > display.get_width()):
            if not end_game:
                death_s.play()
                circle_effects.append([player_pos, 6, [6, 0.15], [10, 0.2], (190, 40, 100)])
                circle_effects.append([player_pos, 6, [6, 0.05], [5, 0.04], (190, 40, 100)])
                screen_shake = 12
            end_game = True

        # GUI ---------------------------------------------------- #
        font.render('score: ' + str(int(game_score)), gui_display, (game_text_loc, 4))
        font.render('press space to pause', gui_display, (game_text_loc, 20))
        font2.render(str(int(game_score)), gui_display,
                     (display.get_width() // 2 - font.width(str(int(game_score))) // 2, end_text_loc + 4))
        font2.render('press R', gui_display, (display.get_width() // 2 - font.width('press R') // 2, end_text_loc + 28))
        font.render(str(int(game_score)), gui_display,
                    (display.get_width() // 2 - font.width(str(int(game_score))) // 2, end_text_loc))
        font.render('press R to restart', gui_display,
                    (display.get_width() // 2 - font.width('press R to restart') // 2, end_text_loc + 24))
        font.render('press M for main menu', gui_display,
                    (display.get_width() // 2 - font.width('press M for main menu') // 2, end_text_loc + 40))

        if end_game:
            game_text_loc += (-220 - game_text_loc) / 20
            end_text_loc += (200 - end_text_loc) / 20
        else:
            game_text_loc += (6 - game_text_loc) / 10
            end_text_loc += (-220 - end_text_loc) / 20

        # Buttons ------------------------------------------------ #
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:  # trong trường hợp bấm nút
                if event.key == K_m:  # bấm m = menu
                    if end_game:
                        pygame.event.set_grab(False)
                        click_s.play()
                        fade()
                        main_menu()
                if event.key == K_SPACE:  # bấm m = menu
                    if not end_game:
                        pause()
                if event.key == K_r:  # bấm r để restart trong trường hợp thua đặt lại các giá trị
                    if end_game:
                        restart_s.play()
                        transition = 30
                        sparks = []
                        player_path = []
                        game_score = 0
                        end_game = False
                        particles = []
                        platforms = [[[0, display.get_height() - 1], [display.get_width(), display.get_height() - 1]]]
                        last_point = [display.get_width() // 2, display.get_height()]
                        scroll = 0
                        player_pos = [display.get_width() // 2, display.get_height() // 2]
                        player_velocity = [0, 0]
                        circle_effects = []
                        last_place = 50
            if event.type == MOUSEBUTTONDOWN:  # bấm chuột để tạo điểm kẻ đường thẳng
                if event.button == 1:
                    if not end_game:
                        line = [last_point, [mx, my + scroll]]
                        line.sort()
                        platforms.append(line)
                        last_point = [mx, my + scroll]
                        circle_effects.append([[mx, my + scroll], 4, [4, 0.2], [4, 0.3], (255, 255, 255)])
                        click_s.play()

        # Update cửa sổ ------------------------------------------------- #
        display_background = display.copy()
        black_surf = pygame.Surface(screen.get_size())
        black_surf.fill(background_color)
        display.set_colorkey(background_color)
        screen.blit(
            pygame.transform.scale(display_background, (display.get_width() * 2 + 40, display.get_height() * 2 + 40)),
            (-20 + BORDER_WIDTH, 0))
        screen.blit(black_surf, (0, 0))
        offset = [0, 0]
        if screen_shake:  # hiệu ứng rung màn hình khi screen_shake = true
            offset[0] += random.randint(0, 10) - 5
            offset[1] += random.randint(0, 10) - 5
        screen.blit(pygame.transform.scale(display, (display.get_width() * 2, display.get_height() * 2)),
                    (BORDER_WIDTH + offset[0], offset[1]))
        screen.blit(pygame.transform.scale(gui_display, (display.get_width() * 2, display.get_height() * 2)),
                    (BORDER_WIDTH, 0))
        border_box = pygame.Rect(0, 0, BORDER_WIDTH, screen.get_height())
        pygame.draw.rect(screen, (0, 0, 0), border_box)
        border_box.x = screen.get_width() - BORDER_WIDTH
        pygame.draw.rect(screen, (0, 0, 0), border_box)
        if transition:
            black_surf = pygame.Surface(screen.get_size())
            black_surf.set_alpha(255 * transition / 30)
            screen.blit(black_surf, (0, 0))
        pygame.display.update()
        mainClock.tick(60)


main_menu()
