import pygame
import random
import math
import time
import os
import winsound  # For sound effects

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

class Laser:
    def __init__(self, x, y, speed, is_enemy, damage, width=5):
        self.x = x
        self.y = y
        self.speed = speed
        self.is_enemy = is_enemy
        self.damage = damage
        self.width = width
        self.height = 15

    def move(self):
        self.y += self.speed

    def draw(self, screen):
        color = RED if self.is_enemy else GREEN
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))

class Enemy:
    def __init__(self, x, y, enemy_type):
        self.x = x
        self.y = y
        self.enemy_type = enemy_type
        self.width = 40
        self.height = 40
        self.speed = 3
        self.health = 30
        self.shoot_counter = 0

    def move(self):
        self.y += self.speed

    def shoot(self):
        self.shoot_counter += 1
        if self.shoot_counter >= 100:
            self.shoot_counter = 0
            laser = Laser(self.x + self.width / 2, self.y + self.height, 5, True, 10)
            return laser
        return None

    def draw(self, screen):
        pygame.draw.polygon(screen, RED, [
            (self.x + self.width / 2, self.y),
            (self.x, self.y + self.height / 2),
            (self.x + self.width, self.y + self.height / 2)
        ])
        pygame.draw.rect(screen, RED, (self.x, self.y + self.height / 2, self.width, self.height / 2))

class Player:
    def __init__(self):
        self.x = WINDOW_WIDTH / 2 - 20
        self.y = WINDOW_HEIGHT - 60
        self.width = 40
        self.height = 40
        self.speed = 5
        self.health = 100
        self.score = 0

    def shoot(self):
        laser = Laser(self.x + self.width / 2, self.y, -10, False, 25)
        return [laser]

    def draw(self, screen):
        pygame.draw.polygon(screen, GREEN, [
            (self.x + self.width / 2, self.y),
            (self.x, self.y + self.height / 2),
            (self.x + self.width, self.y + self.height / 2)
        ])
        pygame.draw.rect(screen, GREEN, (self.x, self.y + self.height / 2, self.width, self.height / 2))

class Powerup:
    def __init__(self, x, y, type):
        self.x = x
        self.y = y
        self.type = type
        self.width = 20
        self.height = 20
        self.speed = 3

    def move(self):
        self.y += self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, YELLOW, (self.x, self.y, self.width, self.height))

class Star:
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.speed = speed

    def move(self):
        self.y += self.speed
        if self.y > WINDOW_HEIGHT:
            self.y = -10
            self.x = random.randint(0, WINDOW_WIDTH)

    def draw(self, screen):
        pygame.draw.circle(screen, WHITE, (self.x, self.y), 2)

class Level:
    def __init__(self, level_number):
        self.level_number = level_number
        self.enemies = []
        self.lasers = []
        self.powerups = []
        self.start_time = time.time()
        self.duration = 60  # seconds
        self.enemy_spawn_rate = 100

    def spawn_powerup(self):
        if random.randint(0, 1000) == 0:
            powerup_type = 'rapid_fire'
            powerup_x = random.randint(0, WINDOW_WIDTH - 20)
            self.powerups.append(Powerup(powerup_x, -20, powerup_type))

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Star Wars Space Shooter")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 32)
        self.state = "MENU"
        self.current_level = None
        self.level_number = 1
        self.player = Player()
        self.stars = [Star(random.randint(0, WINDOW_WIDTH), random.randint(0, WINDOW_HEIGHT), random.randint(1, 3)) for _ in range(200)]
        self.running = True
        self.unlocked_levels = 1

    def start_level(self, level_number):
        self.level_number = level_number
        self.current_level = Level(level_number)
        self.current_level.start_time = time.time()
        self.state = "PLAYING"
        self.player.health = 100
        self.player.score = 0

    def handle_collisions(self):
        for laser in self.current_level.lasers[:]:
            if not laser.is_enemy:
                for enemy in self.current_level.enemies[:]:
                    if (laser.x < enemy.x + enemy.width and
                        laser.x + laser.width > enemy.x and
                        laser.y < enemy.y + enemy.height and
                        laser.y + laser.height > enemy.y):
                        enemy.health -= laser.damage
                        print("Enemy health: ", enemy.health)
                        if enemy.health <= 0:
                            self.current_level.enemies.remove(enemy)
                            self.player.score += 100
                        self.current_level.lasers.remove(laser)
            else:
                if (laser.x < self.player.x + self.player.width and
                    laser.x + laser.width > self.player.x and
                    laser.y < self.player.y + self.player.height and
                    laser.y + laser.height > self.player.y):
                    self.player.health -= laser.damage
                    self.current_level.lasers.remove(laser)
                    if self.player.health <= 0:
                        self.state = "GAME_OVER"

    def handle_powerup_collision(self):
        for powerup in self.current_level.powerups[:]:
            if (self.player.x < powerup.x + powerup.width and
                powerup.x < self.player.x + self.player.width and
                self.player.y < powerup.y + powerup.height and
                powerup.y < self.player.y + self.player.height):
                if powerup.type == 'rapid_fire':
                    # Implement rapid fire effect
                    pass
                self.current_level.powerups.remove(powerup)

    def update_level(self):
        if time.time() - self.current_level.start_time >= self.current_level.duration:
            self.state = "LEVEL_COMPLETE"
            if self.level_number < 10:
                self.unlocked_levels += 1
            else:
                self.state = "VICTORY"

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if self.state == "MENU":
                            mouse_x, mouse_y = pygame.mouse.get_pos()
                            for i in range(1, 11):
                                pos_x = (i-1) % 5 * 200 + 100
                                pos_y = (i-1) // 5 * 100 + 300
                                if (pos_x < mouse_x < pos_x + 100 and
                                    pos_y < mouse_y < pos_y + 50 and
                                    i <= self.unlocked_levels):
                                    self.start_level(i)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and self.state == "PLAYING":
                        new_lasers = self.player.shoot()
                        if new_lasers:
                            self.current_level.lasers.extend(new_lasers)
                            winsound.Beep(1000, 50)  # Laser sound
                    elif event.key == pygame.K_ESCAPE:
                        self.state = "MENU"

            if self.state == "PLAYING":
                keys = pygame.key.get_pressed()
                if keys[pygame.K_LEFT] and self.player.x > 0:
                    self.player.x -= self.player.speed
                if keys[pygame.K_RIGHT] and self.player.x < WINDOW_WIDTH - self.player.width:
                    self.player.x += self.player.speed
                if keys[pygame.K_UP] and self.player.y > 0:
                    self.player.y -= self.player.speed
                if keys[pygame.K_DOWN] and self.player.y < WINDOW_HEIGHT - self.player.height:
                    self.player.y += self.player.speed

                if random.randint(0, self.current_level.enemy_spawn_rate) == 0:
                    x = random.randint(0, WINDOW_WIDTH - 40)
                    self.current_level.enemies.append(Enemy(x, -50, 'tie_fighter'))

                for enemy in self.current_level.enemies[:]:
                    enemy.move()
                    new_laser = enemy.shoot()
                    if new_laser:
                        self.current_level.lasers.append(new_laser)

                for laser in self.current_level.lasers[:]:
                    laser.move()
                    if (laser.y < -10 or laser.y > WINDOW_HEIGHT + 10 or
                        laser.x < -10 or laser.x > WINDOW_WIDTH + 10):
                        self.current_level.lasers.remove(laser)

                self.current_level.spawn_powerup()

                for powerup in self.current_level.powerups[:]:
                    powerup.move()
                    if powerup.y > WINDOW_HEIGHT:
                        self.current_level.powerups.remove(powerup)

                self.handle_powerup_collision()
                self.handle_collisions()
                self.update_level()

            self.screen.fill(BLACK)
            for star in self.stars:
                star.move()
                star.draw(self.screen)

            if self.state == "MENU":
                title = self.font.render("STAR WARS SPACE SHOOTER", True, YELLOW)
                self.screen.blit(title, (WINDOW_WIDTH/2 - title.get_width()/2, 100))
                instruction = self.font.render("Click level to start", True, WHITE)
                self.screen.blit(instruction, (WINDOW_WIDTH/2 - instruction.get_width()/2, 200))
                for i in range(1, 11):
                    color = WHITE if i <= self.unlocked_levels else (100, 100, 100)
                    text = self.font.render(f"Level {i}", True, color)
                    pos_x = (i-1) % 5 * 200 + 100
                    pos_y = (i-1) // 5 * 100 + 300
                    self.screen.blit(text, (pos_x, pos_y))

            elif self.state == "PLAYING":
                self.player.draw(self.screen)
                for enemy in self.current_level.enemies:
                    enemy.draw(self.screen)
                for laser in self.current_level.lasers:
                    laser.draw(self.screen)
                for powerup in self.current_level.powerups:
                    powerup.draw(self.screen)

                # Health Bar
                health_bar_width = (self.player.health / 100) * 200
                pygame.draw.rect(self.screen, RED, (10, 10, 200, 20))
                pygame.draw.rect(self.screen, GREEN, (10, 10, health_bar_width, 20))

                score_text = self.font.render(f"Score: {self.player.score}", True, WHITE)
                level_text = self.font.render(f"Level: {self.level_number}", True, WHITE)
                time_left = max(0, self.current_level.duration - (time.time() - self.current_level.start_time))
                time_text = self.font.render(f"Time: {int(time_left)}s", True, WHITE)
                self.screen.blit(score_text, (10, 40))
                self.screen.blit(level_text, (10, 70))
                self.screen.blit(time_text, (10, 100))

            elif self.state == "GAME_OVER":
                text = self.font.render("GAME OVER - Press ESC for Menu", True, RED)
                self.screen.blit(text, (WINDOW_WIDTH/2 - text.get_width()/2, WINDOW_HEIGHT/2))
                winsound.Beep(500, 200)  # Explosion sound

            elif self.state == "LEVEL_COMPLETE":
                text = self.font.render(f"Level {self.level_number} Complete! Press ESC for Menu", True, GREEN)
                self.screen.blit(text, (WINDOW_WIDTH/2 - text.get_width()/2, WINDOW_HEIGHT/2))
                winsound.Beep(1000, 100)  # Level complete sound

            elif self.state == "VICTORY":
                text = self.font.render("Congratulations! You've beaten the game! Press ESC for Menu", True, YELLOW)
                self.screen.blit(text, (WINDOW_WIDTH/2 - text.get_width()/2, WINDOW_HEIGHT/2))
                winsound.Beep(1500, 150)  # Victory sound

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
