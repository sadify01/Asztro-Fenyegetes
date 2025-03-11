import pygame
import sys
import random
from settings import *

pygame.init()
window = pygame.display.set_mode((monitor_width, monitor_height), pygame.FULLSCREEN)
pygame.display.set_caption("Asztro Fenyegetés")
font = pygame.font.SysFont("Calibri", int(unit), bold=True)
pygame.mouse.set_visible(False)
clock = pygame.time.Clock()
previous_time = pygame.time.get_ticks() / 1000

game_active = False
game_lost = False
game_won = False

enemies = []
bullets = []


class Background:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.width = monitor_width
        self.height = monitor_height
        self.image = pygame.image.load("assets/bg.png").convert()
        self.image = pygame.transform.scale(self.image, (self.width, self.height))


    def draw(self):
        for i in range(2):
            window.blit(self.image, (self.x, self.y - i * monitor_height))


    def update(self):
        self.y += base_speed * dt / 15
        if self.y > monitor_height:
            self.y = 0


class Player:
    def __init__(self):
        self.x = monitor_width / 2 - spaceship_size / 2
        self.y = monitor_width / 2
        self.width = spaceship_size
        self.height = spaceship_size
        self.speed = base_speed
        self.damage = 25
        self.hp = 1000
        self.max_hp = 1000
        self.image = pygame.image.load("assets/player.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.width, self.height))
        self.mask = pygame.mask.from_surface(self.image)
        self.healthbar = HealthBar(monitor_width - unit * 2 - unit / 15 * 2, unit / 15 * 2, unit * 2, unit / 15 * 2, self.max_hp)
        self.last_shot_time = 0


    def draw(self):
        window.blit(self.image, (self.x, self.y))
        self.healthbar.draw()


    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.y -= self.speed * dt
        if keys[pygame.K_s]:
            self.y += self.speed * dt
        if keys[pygame.K_a]:
            self.x -= self.speed * dt
        if keys[pygame.K_d]:
            self.x += self.speed * dt
        if self.x < 0:
            self.x = 0
        if self.x > monitor_width - spaceship_size:
            self.x = monitor_width - spaceship_size
        if self.y < unit * 3:
            self.y = unit * 3
        if self.y > monitor_height - spaceship_size:
            self.y = monitor_height - spaceship_size
        
        self.healthbar.hp = self.hp
        self.healthbar.update()


    def shoot(self, current_time):
        if current_time - self.last_shot_time >= 0.25:
            bullet = Bullet(self.x + self.width / 2, self.y, 1, 1, "player", self.damage)
            bullets.append(bullet)
            self.last_shot_time = current_time


class HealthBar:
    def __init__(self, x, y, width, height, max_hp):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.hp = max_hp
        self.max_hp = max_hp
        self.color = "green"


    def draw(self):
        ratio = self.hp / self.max_hp
        pygame.draw.rect(window, "dimgrey", (self.x, self.y, self.width, self.height))
        pygame.draw.rect(window, self.color, (self.x, self.y, self.width * ratio, self.height))


    def update(self):
        if self.hp > self.max_hp * 0.5:
            self.color = "green"
        elif self.hp > self.max_hp * 0.25:
            self.color = "yellow"
        else:
            self.color = "red"


class Enemy:
    def __init__(self, x, y, width, height, damage, max_hp, image):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.hp = max_hp
        self.max_hp = max_hp
        self.damage = damage
        self.image = pygame.image.load(f"assets/{image}").convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.width, self.height))
        self.mask = pygame.mask.from_surface(self.image)
        self.speed = base_speed / 5
        self.healthbar = HealthBar(self.x, self.y, self.width, unit / 15, self.max_hp)
        self.last_shot_time = 0


    def draw(self):
        window.blit(self.image, (self.x, self.y))
        if self.hp != self.max_hp:
            self.healthbar.draw()


    def update(self):
        self.y += self.speed * dt
        self.healthbar.x = self.x
        self.healthbar.y = self.y - 5
        self.healthbar.hp = self.hp
        self.healthbar.update()
        if self.y > monitor_height:
            enemies.remove(self)
    

    def shoot(self, current_time):
        if game_lost == False:
            if current_time - self.last_shot_time >= 2:
                bullet = Bullet(self.x + self.width / 2, self.y + self.height, 2, -1, "enemy", self.damage)
                bullets.append(bullet)
                self.last_shot_time = current_time


class Bullet:
    def __init__(self, x, y, image, direction, owner, damage):
        self.x = x
        self.y = y
        self.width = unit * 0.05
        self.height = unit * 0.3
        self.image = pygame.image.load(f"assets/bullet{image}.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.width, self.height))
        self.mask = pygame.mask.from_surface(self.image)
        self.speed = base_speed * 2
        self.direction = direction
        self.owner = owner
        self.damage = damage


    def draw(self):
        window.blit(self.image, (self.x, self.y))


    def update(self):
        self.y -= self.speed * dt * self.direction
        if self.y < 0 - self.height or self.y > monitor_height:
            bullets.remove(self)


def draw_text(text, font, color, x, y):
    image = font.render(text, True, color)
    text_rect = image.get_rect(center=(x, y))
    window.blit(image, text_rect.topleft)


for i in range(0, 20):
    enemy = Enemy(x=random.randint(int(unit * 2), int(monitor_width - unit * 3 - unit / 15 * 2)),
                  y=-spaceship_size - i * spaceship_size * 2,
                  width=spaceship_size,
                  height=spaceship_size,
                  damage=25,
                  max_hp=100,
                  image="enemy1.png")
    enemies.append(enemy)

enemy = Enemy(x=monitor_width / 2 - spaceship_size * 1,
              y=-spaceship_size - 21 * spaceship_size * 2,
              width=spaceship_size * 2,
              height=spaceship_size * 2,
              damage=250,
              max_hp=500,
              image="enemy4.png")
enemies.append(enemy)

for i in range(22, 40):
    enemy = Enemy(x=random.randint(int(unit * 2), int(monitor_width - unit * 3 - unit / 15 * 2)),
                  y=-spaceship_size - i * spaceship_size * 2,
                  width=spaceship_size,
                  height=spaceship_size,
                  damage=50,
                  max_hp=150,
                  image="enemy2.png")
    enemies.append(enemy)

enemy = Enemy(x=monitor_width / 2 - spaceship_size * 2,
              y=-spaceship_size - 42 * spaceship_size * 2,
              width=spaceship_size * 4,
              height=spaceship_size * 4,
              damage=500,
              max_hp=1000,
              image="enemy5.png")
enemies.append(enemy)

for i in range(43, 60):
    enemy = Enemy(x=random.randint(int(unit * 2), int(monitor_width - unit * 3 - unit / 15 * 2)),
                  y=-spaceship_size - i * spaceship_size * 2,
                  width=spaceship_size,
                  height=spaceship_size,
                  damage=100,
                  max_hp=200,
                  image="enemy3.png")
    enemies.append(enemy)

enemy = Enemy(x=monitor_width / 2 - spaceship_size * 2,
              y=-spaceship_size - 62 * spaceship_size * 2,
              width=spaceship_size * 4,
              height=spaceship_size * 4,
              damage=1000,
              max_hp=2000,
              image="enemy6.png")
enemies.append(enemy)

background = Background()
player = Player()

while True:
    current_time = pygame.time.get_ticks() / 1000
    dt = current_time - previous_time
    previous_time = current_time
    clock.tick(refresh_rate)

    event = pygame.event.poll()
    if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()

    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit()
        
        if event.key == pygame.K_SPACE:
            game_active = True

    background.update()
    background.draw()

    if player.hp > 0:
        if enemies == []:
            game_won = True

    for bullet in bullets:
        bullet.update()
        bullet.draw()

    if game_active == True:        
        for enemy in enemies:
            enemy.update()
            if enemy.y > 0 - enemy.height / 1.5:
                enemy.shoot(current_time)
            enemy.draw()
        
        if game_lost == False:
            player.update()
            mouse_buttons = pygame.mouse.get_pressed()
            if mouse_buttons[0]:
                player.shoot(current_time)
        else:
            draw_text("Sikertelen misszió", font, (255, 150, 150), monitor_width / 2, monitor_height / 2)
    
    if game_active == False:
        draw_text("Nyomd meg az ŰR gombot", font, (150, 150, 255), monitor_width / 2, monitor_height / 2)

    for bullet in bullets[:]:
        bullet_rect = pygame.Rect(bullet.x, bullet.y, bullet.width, bullet.height)
        
        if bullet.owner == "player":
            for enemy in enemies[:]:
                enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)
                if bullet_rect.colliderect(enemy_rect):
                    offset = (int(enemy.x - bullet.x), int(enemy.y - bullet.y))
                    if bullet.mask.overlap(enemy.mask, offset):
                        bullets.remove(bullet)
                        enemy.hp -= bullet.damage
                        if enemy.hp <= 0:
                            enemies.remove(enemy)
                        break
        
        if bullet.owner == "enemy":
            player_rect = pygame.Rect(player.x, player.y, player.width, player.height)
            if bullet_rect.colliderect(player_rect):
                offset = (int(player.x - bullet.x), int(player.y - bullet.y))
                if bullet.mask.overlap(player.mask, offset):
                    bullets.remove(bullet)
                    player.hp -= bullet.damage
                    if player.hp <= 0 and game_lost == False:
                        game_lost = True

    if game_lost == False:
        player.draw()
    
    if game_won:
        draw_text("Sikeres misszió", font, (150, 255, 150), monitor_width / 2, monitor_height / 2)

    pygame.display.update()
