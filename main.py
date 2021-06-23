import pygame
import pickle
#you could use the socket module because we are using this to read a data_file
from os import path
pygame.init()
title_size = 48
cols = 15
margin = 70
SCREEN_WIDTH = title_size * cols
SCREEN_HEIGHT = (title_size * cols) + margin
BG = (255, 199, 172)
score = 0
icon = pygame.image.load("icon.png")
pygame.display.set_caption("Red's adventure")
pygame.display.set_icon(icon)

game_over = 0
mmnu = True
level = 1
font_score = pygame.font.SysFont("Courier", 20)
scr = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
e_btn = pygame.image.load("Assets/Res_button/1.png")
s_btn = pygame.image.load("Assets/Res_button/2.png")

moving_left = False
moving_right = False

rate = pygame.time.Clock()
FPS = 60


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    scr.blit(img, (x, y))


def reset(level):
    player.reset(100, SCREEN_HEIGHT - 130, "MC animation", 2)
    enemy_group.empty()
    sludge_group.empty()
    p_group.empty()
    if path.exists(f"level{level}_data"):
        pickle_in = open(f"level{level}_data", "rb")
        world = pickle.load(pickle_in)
    w = World(world)
    return w


class Button():
    def __init__(self, x, y, img):
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

    def draw(self):
        action = False
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked= False
        scr.blit(self.image, self.rect)
        return action


class Player():
    def __init__(self, x, y, dir, s):
        self.reset(x, y, dir, s)

    def draw(self, game_over, value, condition_jump, condition_left, condition_right):
        dx = 0
        dy = 0
        walk_cooldown = 1
        if game_over == 0:
            if condition_jump and self.jumped == False and self.in_air == False:
                self.vel_y_comp = -15
                self.jumped = True
            if condition_jump == False:
                self.jumped = False
            if condition_left:
                dx -= 2
                self.flip = True
                self.direction = -1
                self.counter += 1
            if condition_right:
                dx += 2
                self.direction = 1
                self.flip = False
                self.counter += 1
            if self.counter > walk_cooldown:
                self.index += 1
                if self.index >= len(self.imgs):
                    self.index = 0
            if condition_left == False and condition_right == False:
                self.counter = 0
                self.index = 0
                self.img = self.imgs[self.index]
            self.img = self.imgs[self.index]
            self.vel_y_comp += 0.8
            if self.vel_y_comp > 10:
                self.vel_y_comp = 10
            dy += self.vel_y_comp
            self.in_air = True
            for tile in w.tile_list:
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    if self.vel_y_comp < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y_comp = 0
                    elif self.vel_y_comp >= 0:
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y_comp = 0
                        self.in_air = False

            if pygame.sprite.spritecollide(self, enemy_group, False):
                game_over = -1
            if pygame.sprite.spritecollide(self, sludge_group, False):
                game_over = -1
            if pygame.sprite.spritecollide(self, p_group, False) and value:
                game_over = 1

        elif game_over == -1:
            self.img = self.dead_img
            if self.rect.y > 50:
                self.rect.y -= 10

        self.rect.x += dx
        self.rect.y += dy

        scr.blit(pygame.transform.flip(self.img, self.flip, False), self.rect)
        return game_over

    def reset(self, x, y, dir, s):
        self.imgs = []
        self.index = 0
        self.direction = 1
        self.counter = 0
        for i in range(0, 20):
            img_right = pygame.image.load(f"Assets/{dir}/{i}.png")
            img_right = pygame.transform.scale(img_right, (img_right.get_width() * s, img_right.get_height() * s))
            self.imgs.append(img_right)
        self.dead_img = pygame.image.load("Assets/Death/0.png")
        self.img = self.imgs[self.index]
        self.flip = False
        self.rect = self.img.get_rect()
        self.width = self.img.get_width()
        self.height = self.img.get_height()
        self.rect.x = x
        self.rect.y = y
        self.vel_y_comp = 0
        self.jumped = False
        self.in_air = True


enemy_group = pygame.sprite.Group()


class World():
    def __init__(self, data):
        self.tile_list = []
        dirt_img = pygame.image.load("Assets/bg/dirt.png")
        grass_img = pygame.image.load("Assets/bg/grass.png")
        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:
                    img = pygame.transform.scale(dirt_img, (title_size, title_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * title_size
                    img_rect.y = row_count * title_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 2:
                    img = pygame.transform.scale(grass_img, (title_size, title_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * title_size
                    img_rect.y = row_count * title_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 3:
                    enemy = Enemy(col_count * title_size, row_count * title_size + 25)
                    enemy_group.add(enemy)
                if tile == 4:
                    sludge = Sludge(col_count * title_size, row_count * title_size + (title_size // 2))
                    sludge_group.add(sludge)
                if tile == 5:
                    portal = Portal(col_count * title_size, row_count * title_size)
                    p_group.add(portal)
                if tile == 6:
                    coin = Coin(col_count * title_size, row_count * title_size)
                    coin_group.add(coin)
                col_count += 1
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            scr.blit(tile[0], tile[1])


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("Assets/E1 animation/0.png")
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0

    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter *= -1



class Sludge(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        image = pygame.image.load("Assets/Sludge/0.png")
        self.image = pygame.transform.scale(image, (title_size, title_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        image = pygame.image.load("Assets/Point/0.png")
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Portal(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        image = pygame.image.load("Assets/Res_button/portal.png")
        self.image = pygame.transform.scale(image, (title_size, int(title_size * 1.5)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        self.dx = 0
        self.imgs = []
        self.index = 0
        pygame.sprite.Sprite.__init__(self)
        for i in range(0, 14):
            image = pygame.image.load(f"Assets/sun/{i}.png")
            self.imgs.append(image)
        self.img = self.imgs[self.index]
        self.rect = self.img.get_rect()
        self.rect.x = x
        self.rect.y = y

    def fire(self):
        key = pygame.key.get_pressed()
        if game_over == 0:
            if key[pygame.K_1]:
                scr.blit(self.img, (self.rect.x, self.rect.y))
                self.index += 1


x = 200

player = Player(75, 627, "MC animation", 2)

r_button = pygame.image.load("Assets/Res_button/0.png")
sludge_group = pygame.sprite.Group()
p_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
if path.exists(f"level{level}_data"):
    pickle_in = open(f"level{level}_data", "rb")
    world = pickle.load(pickle_in)

w = World(world)
res_button = Button(SCREEN_WIDTH//2 + 210, SCREEN_HEIGHT//2 - 300, r_button)
start_button = Button(SCREEN_WIDTH//2 - 115, SCREEN_HEIGHT//2 - 100, s_btn)
exit_button = Button(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 100, e_btn)
score_coin = Coin(title_size//2, title_size//2 + 20)
coin_group.add(score_coin)
run = True
shoot = False
max_level = 2
while run:
    bullet = Bullet(player.rect.centerx, player.rect.centery - 40)
    rate.tick(FPS)
    scr.fill(BG)
    if mmnu == True:
        if start_button.draw() == True:
            mmnu = False
        if exit_button.draw() == True:
            run = False
    elif mmnu == False:
        w.draw()
        key = pygame.key.get_pressed()
        if game_over == 0:
            enemy_group.update()
            if pygame.sprite.spritecollide(player, coin_group, True):
                score += 1
            draw_text("X " + str(score), font_score, (255, 255, 255), title_size, title_size - 7)
        enemy_group.draw(scr)
        sludge_group.draw(scr)
        key = pygame.key.get_pressed()
        game_over = player.draw(game_over, True, key[pygame.K_w], key[pygame.K_a], key[pygame.K_d])
        bullet.fire()
        p_group.draw(scr)
        coin_group.draw(scr)
        if game_over == -1:
            if res_button.draw():
                world = []
                w = reset(level)
                player.reset(75, 627, "MC animation", 2)
                game_over = 0
                score = 0
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE] == True or key[pygame.K_z] == True:
                world = []
                w = reset(level)
                player.reset(75, 627, "MC animation", 2)
                game_over = 0
                score = 0
        if game_over == 1:
            if level < max_level:
                level += 1
                world = []
                w = reset(level)
                game_over = 0
            else:
                level = 0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        key = pygame.key.get_pressed()
        if key[pygame.K_ESCAPE] == True:
            run = False
    pygame.display.update()
pygame.quit()
