import pygame
import sys
from copy import deepcopy
from random import choice
import sqlite3
import os

# здесь определяются константы,
# классы и функции
con = sqlite3.connect("profiles.db")
cur = con.cursor()
cursor = 1
added = False
bombs = 5
stick = 5
hstmp = cur.execute("""SELECT H_Score FROM profiles""").fetchall()
money = cur.execute("""SELECT money FROM profiles""").fetchall()
hs = int(hstmp[0][0])
money = int(money[0][0])
W, H, TILE = 15, 25, 20
window = 0
size = width, height = (W * TILE) + 160, H * TILE
FPS = 10
frst = True
pause = False
# здесь происходит инициация,
# создание объектов
os.environ['SDL_VIDEO_WINDOW_POS'] = '150,150'
pygame.init()
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
grid = [pygame.Rect(x * TILE, y * TILE, TILE, TILE) for x in range(W) for y in range(H)]
figures = [[(-1, 0), (-2, 0), (-1, 1), (0, 0), (0, -1)],
           [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)],
           [(0, 1), (1, 1), (-1, 0), (0, 0), (-1, -1)],
           [(-1, 0), (-2, -1), (-2, 0), (0, 0), (0, -1)],
           [(-1, 0), (-2, -1), (-1, 1), (0, -1), (-1, -1)],
           [(-1, 1), (-1, -1), (-1, 0), (0, 1), (1, 1)],
           [(0, 0), (-1, -1), (0, -1), (-1, 0), (1, 0)],
           [(0, 0), (-1, -1), (0, -1), (-1, 0), (-2, 0)],
           [(0, 0), (0, -1), (1, -1), (0, 1), (-1, 1)],
           [(0, 0), (0, -1), (-1, -1), (0, 1), (1, 1)],
           [(-1, 0), (-2, 0), (-1, 1), (0, 0), (-2, -1)],
           [(0, 0), (-2, -1), (-1, -1), (-1, 0), (1, 0)],
           [(0, 0), (0, -1), (1, -1), (-1, 0), (-2, 0)],
           [(0, 1), (0, 2), (-1, 0), (0, 0), (0, -1)],
           [(1, 0), (0, -1), (0, 1), (0, 0), (0, 2)],
           [(-1, 0), (-2, 0), (-2, -1), (0, 0), (1, 0)],
           [(-1, -1), (-2, -1), (-2, 0), (0, -1), (1, -1)],
           [(0, 0), (-2, 0), (-1, 0), (1, 0), (2, 0)]]
figs = [[pygame.Rect(x + W // 2, y + 1, 1, 1) for x, y in fig_pos] for fig_pos in figures]
figure_rect = pygame.Rect(0, 0, TILE - 2, TILE - 2)
count, speed, end_sum, is_sp_up = 0, 200, 2000, False
field = [[0 for i in range(W)] for j in range(H)]
font = pygame.font.Font(None, 30)
score = 0
text = font.render("score:", True, (255, 255, 255))
text2 = font.render("High Score:", True, (255, 255, 255))
mode = False
is_regr = False
gm = False
game_speed = 0


def borders():
    if figure[i].x < 0 or figure[i].x > W - 1:
        return False
    elif figure[i].y > H - 1 or field[figure[i].y][figure[i].x]:
        return False
    return True


def moving():
    global window, cursor, frst, move, rot, speed, money, bombs, stick, next_figure, pause
    for i in pygame.event.get():
        if i.type == pygame.QUIT:
            sys.exit()
    keys = pygame.key.get_pressed()
    if window == 1:
        if gm or pause:
            if keys[pygame.K_DOWN]:
                if cursor != 2:
                    cursor += 1
                    frst = False
            elif keys[pygame.K_UP]:
                if cursor != 1:
                    cursor -= 1
                    frst = False
            elif keys[pygame.K_RETURN]:
                if cursor == 1:
                    window = 0
                    cleaning()
                    frst = True
                elif cursor == 2:
                    cleaning()
                    frst = True
        if keys[pygame.K_LEFT]:
            move = -1
        if keys[pygame.K_RIGHT]:
            move = 1
        if keys[pygame.K_DOWN]:
            speed = speed * 2
        if keys[pygame.K_UP]:
            rot = True
        if keys[pygame.K_b]:
            for i in range(H):
                for j in range(W):
                    if field[i][j] != 0:
                        bombs_def(i)
        if keys[pygame.K_s]:
            next_figure = deepcopy(figs[17])
            stick -= 1
        if keys[pygame.K_p]:
            if pause:
                pause = False
            elif not pause:
                pause = True

    elif window == 0:
        if keys[pygame.K_DOWN]:
            if cursor != 3:
                cursor += 1
                frst = False
        elif keys[pygame.K_UP]:
            if cursor != 1:
                cursor -= 1
                frst = False
        elif keys[pygame.K_RETURN]:
            if cursor == 1:
                window = 1
                frst = True
            elif cursor == 2:
                window = 2
                frst = True
            elif cursor == 3:
                sys.exit()
    elif window == 2:
        if keys[pygame.K_RIGHT]:
            if cursor != 2:
                cursor += 1
                frst = False
        elif keys[pygame.K_UP]:
            if cursor != 1:
                cursor -= 1
                frst = False
        elif keys[pygame.K_LEFT]:
            if cursor != 1:
                cursor -= 1
                frst = False
        elif keys[pygame.K_ESCAPE]:
            window = 0
            frst = True
        elif keys[pygame.K_RETURN]:
            if cursor == 1 and money >= 100:
                money -= 100
                bombs += 1
                cur.execute("""UPDATE profiles
                    SET money = ?""", (money,))
                cur.execute("""UPDATE profiles
                                    SET bombs = ?""", (bombs,))
                con.commit()
            elif cursor == 2 and money >= 10:
                money -= 10
                stick += 1
                cur.execute("""UPDATE profiles
                                    SET money = ?""", (money,))
                cur.execute("""UPDATE profiles
                                    SET stick = ?""", (stick,))
                con.commit()


def cleaning():
    global gm, field, score, move, rot, speed, pause, figure, next_figure
    gm = False
    pause = False
    cur.execute("""UPDATE profiles
    SET money = ?""", (money,))
    con.commit()
    field = [[0 for i in range(W)] for j in range(H)]
    score = 0
    move, rot = 0, False
    speed = 400
    figure = deepcopy(choice(figs))
    next_figure = deepcopy(choice(figs))


def bombs_def(h):
    global bombs, field, W, H
    bombs -= 1
    for i in range(h, H):
        for j in range(W):
            field[i][j] = 0



figure = deepcopy(choice(figs))
next_figure = deepcopy(choice(figs))
# главный цикл
while True:
    move, rot = 0, False
    speed = 400 + game_speed * 200
    end_sum = 2000 + game_speed * 150
    screen.fill(pygame.Color('black'))
    # цикл обработки событий
    moving()
    # --------
    # изменение объектов
    # --------
    if window == 1:
        if frst:
            cursor = 1
            screen = pygame.display.set_mode(size)
            gm = False
        text3 = font.render(str(score), True, (255, 255, 255))
        text4 = font.render(str(hs), True, (255, 255, 255))
        screen.blit(text, (320, 40))
        screen.blit(text2, (320, 150))
        screen.blit(text3, (320, 60))
        screen.blit(text4, (320, 170))
        old = deepcopy(figure)
        for i in range(5):
            figure[i].x += move
            if not borders():
                figure = deepcopy(old)
                break
        count += speed
        if count >= end_sum:
            count -= end_sum
            old = deepcopy(figure)
            for i in range(5):
                figure[i].y += 1
                if not borders():
                    for j in range(5):
                        field[old[j].y][old[j].x] = pygame.Color('White')
                    figure = deepcopy(next_figure)
                    next_figure = deepcopy(choice(figs))
                # figure = figs[17]
                    speed = 30
                    break
        center = figure[0]
        if rot:
            for i in range(5):
                x = figure[i].y - center.y
                y = figure[i].x - center.x
                figure[i].x = center.x - x
                figure[i].y = center.y + y
                if not borders():
                    figure = deepcopy(old)
                    break
        line = H - 1
        kol = 0
        for row in range(H - 1, -1, -1):
            count_2 = 0
            for i in range(W):
                if field[row][i]:
                    count_2 += 1
                field[line][i] = field[row][i]
            kol += 1
            if count_2 < W:
                line -= 1
                kol -= 1
        if kol == 1:
            score += 150
        elif 1 < kol < 5:
            score += 150 + round(150 * (1 + kol / 10))
        elif kol == 5:
            score += 150 * 5
            screen.fill(pygame.Color('red'))
            screen.fill(pygame.Color('yellow'))
            screen.fill(pygame.Color('white'))
            screen.fill(pygame.Color('red'))
            screen.fill(pygame.Color('yellow'))
            screen.fill(pygame.Color('white'))
        if score > hs:
            hs = score
            cur.execute("""UPDATE profiles
SET H_Score = ?""", (hs, ))
            con.commit()

        for i_rect in grid:
            pygame.draw.rect(screen, (40, 40, 40), i_rect, 1)

        for i in range(5):
            figure_rect.x = figure[i].x * TILE
            figure_rect.y = figure[i].y * TILE
            pygame.draw.rect(screen, pygame.Color("white"), figure_rect)

        for i in range(5):
            figure_rect.x = next_figure[i].x * TILE + 220
            figure_rect.y = next_figure[i].y * TILE + 260
            pygame.draw.rect(screen, pygame.Color("white"), figure_rect)

        for y, row in enumerate(field):
            for x, col in enumerate(row):
                if col:
                    figure_rect.x, figure_rect.y = x * TILE, y * TILE
                    pygame.draw.rect(screen, col, figure_rect)
        for i in range(W):
            if field[0][i]:
                gm = True

        if gm:
            if not added:
                money += score // 100
            screen.fill(pygame.Color('black'))
            font2 = pygame.font.Font(None, 40)
            text6 = font2.render("Игрушки кончились", True, (255, 255, 255))
            screen.blit(text6, (90, 140))
            text7 = font2.render("Рестарт", True, (255, 255, 255))
            text8 = font2.render("В(На) Меню", True, (255, 255, 255))
            screen.blit(text8, (140, 210))
            screen.blit(text7, (160, 300))
            if cursor == 1:
                pygame.draw.rect(screen, (255, 255, 255), (130, 200, 180, 40), 8)
            if cursor == 2:
                pygame.draw.rect(screen, (255, 255, 255), (150, 290, 120, 40), 8)
        if pause:
            screen.fill(pygame.Color('black'))
            font2 = pygame.font.Font(None, 40)
            text6 = font2.render("Игрушки кончились", True, (255, 255, 255))
            screen.blit(text6, (90, 140))
            text7 = font2.render("Рестарт", True, (255, 255, 255))
            text8 = font2.render("В(На) Меню", True, (255, 255, 255))
            screen.blit(text8, (140, 210))
            screen.blit(text7, (160, 300))
            count = 0
            if cursor == 1:
                pygame.draw.rect(screen, (255, 255, 255), (130, 200, 180, 40), 8)
            if cursor == 2:
                pygame.draw.rect(screen, (255, 255, 255), (150, 290, 120, 40), 8)
        if score >= (game_speed + 1) * 5000:
            game_speed += 1

    elif window == 0:
        if frst:
            cursor = 1
            screen = pygame.display.set_mode(size)
        font2 = pygame.font.Font(None, 80)
        font3 = pygame.font.Font(None, 30)
        text5 = font2.render("Играть", True, (255, 255, 255))
        text6 = font2.render("Магазин", True, (255, 255, 255))
        text7 = font2.render("Выход", True, (255, 255, 255))
        screen.blit(text5, (130, 60))
        screen.blit(text6, (110, 180))
        screen.blit(text7, (130, 300))
        if cursor == 1:
            pygame.draw.rect(screen, (255, 255, 255), (110, 40, 225, 100), 8)
        elif cursor == 2:
            pygame.draw.rect(screen, (255, 255, 255), (90, 160, 270, 90), 8)
        elif cursor == 3:
            pygame.draw.rect(screen, (255, 255, 255), (110, 280, 235, 100), 8)
    elif window == 2:
        if frst:
            cursor = 1
        screen = pygame.display.set_mode((800, 700))
        all_sprites = pygame.sprite.Group()
        sprite = pygame.sprite.Sprite()
        sprite.image = pygame.image.load("bomb3.png")
        sprite.rect = sprite.image.get_rect()
        sprite2 = pygame.sprite.Sprite()
        sprite2.image = pygame.image.load("ropes.png")
        sprite2.rect = sprite.image.get_rect()
        all_sprites.add(sprite)
        all_sprites.add(sprite2)
        sprite.rect.x = 50
        sprite.rect.y = 250
        sprite2.rect.x = 400
        sprite2.rect.y = 250
        if cursor == 1:
            pygame.draw.rect(screen, (255, 255, 255), (40, 240, 160, 160), 8)
        if cursor == 2:
            pygame.draw.rect(screen, (255, 255, 255), (385, 235, 160, 160), 8)
        font2 = pygame.font.Font(None, 60)
        font3 = pygame.font.Font(None, 40)
        text9 = font2.render("Бомба", True, (255, 255, 255))
        text10 = font2.render("Палка", True, (255, 255, 255))
        text11 = font3.render("Цена: 100мон.", True, (255, 255, 255))
        text12 = font3.render("Цена: 10мон.", True, (255, 255, 255))
        text13 = font3.render("Баланс:", True, (255, 255, 255))
        text14 = font3.render(str(money), True, (255, 255, 255))
        screen.blit(text9, (60, 420))
        screen.blit(text10, (400, 420))
        screen.blit(text11, (50, 460))
        screen.blit(text12, (380, 460))
        screen.blit(text13, (500, 40))
        screen.blit(text14, (620, 40))
        # задаём случайное местоположение бомбочке
        all_sprites.draw(screen)
    # обновление экрана
    pygame.display.flip()
    clock.tick(FPS)
