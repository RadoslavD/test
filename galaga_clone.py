import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Simple Invaders Clone")

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
        # Create an "Invaders"-style player ship sprite using pixel art
        self.image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.midbottom = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30)
        self.speed = 0

        # Draw the player ship pixel art (simple invader-like shape)
        # Using green color as before
        green = GREEN
        # Clear surface
        self.image.fill((0, 0, 0, 0))
        # Draw pixels manually to resemble classic invader ship
        pixel_size = 5
        # Coordinates for pixels relative to top-left of image
        pixels = [
            (2, 0), (3, 0),
            (1, 1), (4, 1),
            (0, 2), (1, 2), (2, 2), (3, 2), (4, 2), (5, 2),
            (0, 3), (5, 3),
            (1, 4), (4, 4),
            (2, 5), (3, 5)
        ]
        for (x, y) in pixels:
            pygame.draw.rect(self.image, green, (x * pixel_size, y * pixel_size, pixel_size, pixel_size))

        self.last_shot_time = 0
        self.shoot_delay = 900  # milliseconds, adjusted rate of fire

    def update(self):
        self.rect.x += self.speed
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

    def shoot(self, vx=0):
        bullet = Bullet(self.rect.centerx, self.rect.top, vx)
        return bullet

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, vx=0):
        super().__init__()
        self.image = pygame.Surface((BULLET_WIDTH, BULLET_HEIGHT))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.vx = vx  # horizontal velocity

    def update(self):
        self.rect.y -= BULLET_SPEED
        self.rect.x += self.vx
        if self.rect.bottom < 0 or self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Create an "Invaders"-style enemy sprite using pixel art
        self.image = pygame.Surface((ENEMY_WIDTH, ENEMY_HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.last_shot_time = 0
        self.shoot_delay = 2000  # milliseconds, will decrease with level

        # Draw the enemy pixel art (simple invader-like shape)
        red = RED
        self.image.fill((0, 0, 0, 0))
        pixel_size = 5
        # Coordinates for pixels relative to top-left of image
        pixels = [
            (1, 0), (2, 0), (3, 0), (4, 0),
            (0, 1), (5, 1),
            (0, 2), (1, 2), (2, 2), (3, 2), (4, 2), (5, 2),
            (1, 3), (4, 3),
            (0, 4), (5, 4)
        ]
        for (x_pix, y_pix) in pixels:
            pygame.draw.rect(self.image, red, (x_pix * pixel_size, y_pix * pixel_size, pixel_size, pixel_size))

    def shoot(self):
        bullet = EnemyBullet(self.rect.centerx, self.rect.bottom)
        return bullet

class EnemyGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.direction = 1
        self.speed = ENEMY_SPEED
        self.drop = ENEMY_DROP
        self.speed_increment = 0
        self.dropped = False
        self.create_enemies()

    def create_enemies(self):
        for row in range(ENEMY_ROWS):
            for col in range(ENEMY_COLS):
                enemy = Enemy(50 + col * (ENEMY_WIDTH + 10), 50 + row * (ENEMY_HEIGHT + 10))
                self.add(enemy)

    def update(self, level=1):
        move_sideways = True
        for enemy in self.sprites():
            enemy.rect.x += self.direction * self.speed
            if enemy.rect.right >= SCREEN_WIDTH or enemy.rect.left <= 0:
                move_sideways = False

        if not move_sideways and not self.dropped:
            self.direction *= -1
            for enemy in self.sprites():
                enemy.rect.y += self.drop // 2  # Reduce drop distance to half
            self.dropped = True
        elif move_sideways:
            self.dropped = False

        # Increase speed with level and speed increment
        self.speed = ENEMY_SPEED + (level - 1) * 0.5 + self.speed_increment

# PowerUp settings
POWERUP_WIDTH = 30
POWERUP_HEIGHT = 30
POWERUP_SPEED = 3

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, kind):
        super().__init__()
        self.kind = kind
        self.image = pygame.Surface((POWERUP_WIDTH, POWERUP_HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

        # Draw nicer icons for power-ups
        if kind == "shield":
            # Blue shield icon: circle with a shield shape inside
            blue = (0, 0, 255)
            white = (255, 255, 255)
            center = (POWERUP_WIDTH // 2, POWERUP_HEIGHT // 2)
            radius = POWERUP_WIDTH // 2 - 3
            pygame.draw.circle(self.image, blue, center, radius)
            # Draw a simple shield shape (triangle + rectangle)
            points = [
                (center[0] - 8, center[1] - 4),
                (center[0] + 8, center[1] - 4),
                (center[0] + 4, center[1] + 8),
                (center[0] - 4, center[1] + 8)
            ]
            pygame.draw.polygon(self.image, white, points)
            pygame.draw.line(self.image, blue, (center[0], center[1] - 4), (center[0], center[1] + 8), 2)
        elif kind == "spread_fire":
            # Yellow rapid fire icon: lightning bolt shape
            yellow = (255, 255, 0)
            points = [
                (POWERUP_WIDTH // 2 - 6, POWERUP_HEIGHT // 4),
                (POWERUP_WIDTH // 2 + 2, POWERUP_HEIGHT // 4),
                (POWERUP_WIDTH // 2 - 2, POWERUP_HEIGHT // 2),
                (POWERUP_WIDTH // 2 + 6, POWERUP_HEIGHT // 2),
                (POWERUP_WIDTH // 2 - 2, 3 * POWERUP_HEIGHT // 4),
                (POWERUP_WIDTH // 2 + 2, 3 * POWERUP_HEIGHT // 4),
                (POWERUP_WIDTH // 2 - 6, POWERUP_HEIGHT // 2)
            ]
            pygame.draw.polygon(self.image, yellow, points)
        else:
            # Magenta question mark for unknown power-up
            magenta = (255, 0, 255)
            self.image.fill((0, 0, 0, 0))
            font = pygame.font.SysFont(None, 24)
            text = font.render("?", True, magenta)
            text_rect = text.get_rect(center=(POWERUP_WIDTH // 2, POWERUP_HEIGHT // 2))
            self.image.blit(text, text_rect)

    def update(self):
        self.rect.y += POWERUP_SPEED
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((BULLET_WIDTH, BULLET_HEIGHT))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        self.rect.y += BULLET_SPEED
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

def draw_text(surface, text, x, y):
    img = font.render(text, True, WHITE)
    surface.blit(img, (x, y))

def main():
    player = Player()
    player_group = pygame.sprite.Group(player)

    bullets = pygame.sprite.Group()
    enemies = EnemyGroup()
    powerups = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()

    score = 0
    shield_active = False
    spread_fire_active = False
    spread_fire_timer = 0
    level = 1
    enemy_fire_rate = 2000  # milliseconds, will decrease with level
    last_enemy_shot_time = 0
    player_lives = 3
    enemies_defeated = 0

    running = True

    while running:
        clock.tick(FPS)
        current_time = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.speed = -PLAYER_SPEED
                elif event.key == pygame.K_RIGHT:
                    player.speed = PLAYER_SPEED
                elif event.key == pygame.K_SPACE:
                    current_time = pygame.time.get_ticks()
                    if current_time - player.last_shot_time >= player.shoot_delay:
                        player.last_shot_time = current_time
                        if spread_fire_active:
                            # Shoot multiple bullets rapidly with slight random divergence
                            for _ in range(3):
                                vx = random.uniform(-1.5, 1.5)  # small random horizontal velocity
                                bullet = player.shoot(vx)
                                bullets.add(bullet)
                        else:
                            bullet = player.shoot()
                            bullets.add(bullet)
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT and player.speed < 0:
                    player.speed = 0
                elif event.key == pygame.K_RIGHT and player.speed > 0:
                    player.speed = 0

        player_group.update()
        bullets.update()
        enemies.update(level)
        powerups.update()
        enemy_bullets.update()

        # Check bullet-enemy collisions
        hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
        enemies_defeated += len(hits)
        for enemy in hits:
            # Calculate score based on enemy's vertical position (higher = more points)
            height_factor = max(0, SCREEN_HEIGHT - enemy.rect.top)
            points = int(10 + (height_factor / SCREEN_HEIGHT) * 40)  # base 10 + up to 40 extra points
            score += points

        # Spawn power-ups randomly on enemy destruction
        for enemy in hits:
            if random.random() < 0.1:  # 10% chance to spawn power-up (slightly higher)
                kind = random.choice(["shield", "spread_fire"])
                powerup = PowerUp(enemy.rect.centerx, enemy.rect.centery, kind)
                powerups.add(powerup)
            # Increase speed increment for remaining enemies
            enemies.speed_increment += 0.1

        # Check player-powerup collisions
        powerup_hits = pygame.sprite.spritecollide(player, powerups, True)
        for powerup in powerup_hits:
            if powerup.kind == "shield":
                shield_active = True
            elif powerup.kind == "spread_fire":
                spread_fire_active = True
                spread_fire_timer = pygame.time.get_ticks()

        # Manage rapid fire timer (5 seconds duration)
        if spread_fire_active and pygame.time.get_ticks() - spread_fire_timer > 5000:
            spread_fire_active = False

        # Enemy shooting logic
        if current_time - last_enemy_shot_time > enemy_fire_rate:
            shooting_enemy = random.choice(enemies.sprites()) if enemies.sprites() else None
            if shooting_enemy:
                enemy_bullet = shooting_enemy.shoot()
                enemy_bullets.add(enemy_bullet)
                last_enemy_shot_time = current_time

        # Check enemy bullet-player collisions
        if pygame.sprite.spritecollide(player, enemy_bullets, True):
            if shield_active:
                # Shield absorbs the hit, remove shield
                shield_active = False
            else:
                player_lives -= 1
                # Cancel all power-ups on hit
                shield_active = False
                spread_fire_active = False
                spread_fire_timer = 0
                if player_lives <= 0:
                    running = False

        # Check if enemies reach bottom or collide with player
        for enemy in enemies:
            if enemy.rect.bottom >= SCREEN_HEIGHT:
                running = False
            if pygame.sprite.collide_rect(enemy, player):
                if shield_active:
                    # Shield absorbs the hit, remove shield
                    shield_active = False
                    enemies.remove(enemy)
                else:
                    player_lives -= 1
                    # Cancel all power-ups on hit
                    shield_active = False
                    spread_fire_active = False
                    spread_fire_timer = 0
                    if player_lives <= 0:
                        running = False

        # Check if all enemies are killed to start new level
        if len(enemies) == 0:
            level += 1
            enemies = EnemyGroup()
            enemy_fire_rate = max(500, enemy_fire_rate - 200)  # Increase fire rate, min 500ms

        screen.fill(BLACK)
        player_group.draw(screen)
        bullets.draw(screen)
        enemies.draw(screen)
        powerups.draw(screen)
        enemy_bullets.draw(screen)

        draw_text(screen, f"Score: {score}", 10, 10)
        draw_text(screen, f"Level: {level}", 10, 40)
        draw_text(screen, f"Lives: {player_lives}", 10, 70)
        if shield_active:
            draw_text(screen, "Shield Active", 400, 10)
        if spread_fire_active:
            draw_text(screen, "Spread Fire Active", 400, 40)

        pygame.display.flip()

    # Game over screen with centered text
    screen.fill(BLACK)
    texts = [
        ("Vibe Invaders", 72),
        (f"Final Score: {score}", 36),
        (f"Enemies defeated: {enemies_defeated}", 36),
        ("Vibe coded with OpenAI for $0.48", 24)
    ]
    y = SCREEN_HEIGHT // 3
    for text, size in texts:
        font_obj = pygame.font.SysFont(None, size)
        img = font_obj.render(text, True, WHITE)
        rect = img.get_rect(center=(SCREEN_WIDTH // 2, y))
        screen.blit(img, rect)
        y += size + 20

    pygame.display.flip()

    # Wait for a few seconds before quitting
    pygame.time.wait(5000)
    pygame.quit()
    sys.exit()

    pygame.display.flip()

    # Game over screen with statistics and final message
    screen.fill(BLACK)
    draw_text(screen, "Vibe Invaders", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3, center=True, size=72)
    draw_text(screen, f"Final Score: {score}", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 + 100, center=True)
    draw_text(screen, f"Enemies defeated: {len(hits)}", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 + 140, center=True)
    draw_text(screen, "Vibe coded with OpenAI for $0.57", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 + 200, center=True)
    pygame.display.flip()

    # Wait for a few seconds before quitting
    pygame.time.wait(5000)
    pygame.quit()
    sys.exit()
if __name__ == "__main__":
    main()

# Note: To run this game, you need to have pygame installed.
# You can install it via pip: pip install pygame