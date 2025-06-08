import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Simple Galaga Clone")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Player settings
PLAYER_WIDTH = 50
PLAYER_HEIGHT = 30
PLAYER_SPEED = 5

# Bullet settings
BULLET_WIDTH = 5
BULLET_HEIGHT = 10
BULLET_SPEED = 7

# Enemy settings
ENEMY_WIDTH = 40
ENEMY_HEIGHT = 30
ENEMY_SPEED = 2
ENEMY_DROP = 40
ENEMY_ROWS = 3
ENEMY_COLS = 8

# FPS
FPS = 60
clock = pygame.time.Clock()

# Font
font = pygame.font.SysFont(None, 36)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.midbottom = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30)
        self.speed = 0

    def update(self):
        self.rect.x += self.speed
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        return bullet

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((BULLET_WIDTH, BULLET_HEIGHT))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        self.rect.y -= BULLET_SPEED
        if self.rect.bottom < 0:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((ENEMY_WIDTH, ENEMY_HEIGHT))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

class EnemyGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.direction = 1
        self.speed = ENEMY_SPEED
        self.drop = ENEMY_DROP
        self.create_enemies()

    def create_enemies(self):
        for row in range(ENEMY_ROWS):
            for col in range(ENEMY_COLS):
                enemy = Enemy(50 + col * (ENEMY_WIDTH + 10), 50 + row * (ENEMY_HEIGHT + 10))
                self.add(enemy)

    def update(self):
        move_sideways = True
        for enemy in self.sprites():
            enemy.rect.x += self.direction * self.speed
            if enemy.rect.right >= SCREEN_WIDTH or enemy.rect.left <= 0:
                move_sideways = False

        if not move_sideways:
            self.direction *= -1
            for enemy in self.sprites():
                enemy.rect.y += self.drop

def draw_text(surface, text, x, y):
    img = font.render(text, True, WHITE)
    surface.blit(img, (x, y))

def main():
    player = Player()
    player_group = pygame.sprite.Group(player)

    bullets = pygame.sprite.Group()
    enemies = EnemyGroup()

    score = 0
    running = True

    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.speed = -PLAYER_SPEED
                elif event.key == pygame.K_RIGHT:
                    player.speed = PLAYER_SPEED
                elif event.key == pygame.K_SPACE:
                    bullet = player.shoot()
                    bullets.add(bullet)
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT and player.speed < 0:
                    player.speed = 0
                elif event.key == pygame.K_RIGHT and player.speed > 0:
                    player.speed = 0

        player_group.update()
        bullets.update()
        enemies.update()

        # Check bullet-enemy collisions
        hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
        score += len(hits) * 10

        # Check if enemies reach bottom or collide with player
        for enemy in enemies:
            if enemy.rect.bottom >= SCREEN_HEIGHT:
                running = False
            if pygame.sprite.collide_rect(enemy, player):
                running = False

        screen.fill(BLACK)
        player_group.draw(screen)
        bullets.draw(screen)
        enemies.draw(screen)

        draw_text(screen, f"Score: {score}", 10, 10)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

# Note: To run this game, you need to have pygame installed.
# You can install it via pip: pip install pygame