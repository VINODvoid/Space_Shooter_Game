import pygame
import random
import os
from moviepy.editor import VideoFileClip

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Screen dimensions
SCREEN_WIDTH = 1200  # Increased width
SCREEN_HEIGHT = 900  # Increased height

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Shooter")

# Asset directories
img_dir = os.path.join(os.path.dirname(__file__), 'image')
snd_dir = os.path.join(os.path.dirname(__file__), 'sound')

# Load assets with scaling
player_img = pygame.image.load(os.path.join(img_dir, 'player.png')).convert()
player_img = pygame.transform.scale(player_img, (80, 60))  # Scaled up
enemy_img = pygame.image.load(os.path.join(img_dir, 'enemy.png')).convert()
enemy_img = pygame.transform.scale(enemy_img, (60, 40))  # Scaled up
bullet_img = pygame.image.load(os.path.join(img_dir, 'bullet.png')).convert()
bullet_img = pygame.transform.scale(bullet_img, (16, 32))  # Scaled up

# Load sounds
shoot_sound = pygame.mixer.Sound(os.path.join(snd_dir, 'shoot.wav'))
explosion_sound = pygame.mixer.Sound(os.path.join(snd_dir, 'explosion.wav'))

# Load video
background_video = VideoFileClip("space.mp4")
background_frames = background_video.iter_frames(fps=30, dtype='uint8')
background_frame_iter = iter(background_frames)  # Initialize background frame iterator

# Clock to control frame rate
clock = pygame.time.Clock()

# Font for displaying text
font_name = pygame.font.match_font('arial')

# Function to display text on screen
def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)

# Function to display start menu
def show_start_screen():
    screen.fill(BLACK)
    draw_text(screen, "Space Shooter", 64, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)
    draw_text(screen, "Press any key to start", 36, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYUP:
                waiting = False

# Function to display game over screen
def show_game_over_screen():
    screen.fill(BLACK)
    draw_text(screen, "GAME OVER", 64, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)
    draw_text(screen, "Press any key to play again", 36, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYUP:
                waiting = False

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super(Player, self).__init__()
        self.image = player_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 10
        self.speedx = 0
        self.lives = 3

    def update(self):
        self.speedx = 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.speedx = -5
        if keys[pygame.K_RIGHT]:
            self.speedx = 5
        self.rect.x += self.speedx
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        all_sprites.add(bullet)
        bullets.add(bullet)
        shoot_sound.play()

# Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super(Enemy, self).__init__()
        self.image = enemy_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randint(-100, -40)
        self.speedy = random.randint(1, 2)  # Gradually increase speed
        self.speedx = random.randint(-2, 2)  # Move horizontally
        self.last_shot = pygame.time.get_ticks()  # Track last shot time

    def update(self):
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        if self.rect.top > SCREEN_HEIGHT + 10 or self.rect.left < -25 or self.rect.right > SCREEN_WIDTH + 25:
            self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
            self.rect.y = random.randint(-100, -40)
            self.speedy = random.randint(1, 2)
            self.speedx = random.randint(-2, 2)
        
        # Enemy shoots bullets
        now = pygame.time.get_ticks()
        if now - self.last_shot > 2000:  # Adjust shooting frequency as needed
            self.last_shot = now
            enemy_bullet = Bullet(self.rect.centerx, self.rect.bottom, speed=5, is_enemy_bullet=True)
            all_sprites.add(enemy_bullet)
            enemy_bullets.add(enemy_bullet)

# Bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed=-10, is_enemy_bullet=False):
        super(Bullet, self).__init__()
        self.is_enemy_bullet = is_enemy_bullet
        if self.is_enemy_bullet:
            self.image = pygame.Surface((8, 16))
            self.image.fill(RED)
        else:
            self.image = bullet_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = speed

    def update(self):
        if not self.is_enemy_bullet:
            self.rect.y += self.speedy
            if self.rect.bottom < 0:
                self.kill()
        else:
            self.rect.y += self.speedy
            if self.rect.top > SCREEN_HEIGHT:
                self.kill()

# Initialize player, sprites, and groups
player = Player()
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
all_sprites.add(player)

# Game variables
score = 0  # Initialize score

# Game loop
running = True
show_start_screen()
while running:
    clock.tick(60)

    # Process input (events)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot()

    # Update
    all_sprites.update()

    # Check for collisions
    hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
    for hit in hits:
        explosion_sound.play()
        score += 10  # Increment score on hit
        enemy = Enemy()
        all_sprites.add(enemy)
        enemies.add(enemy)

    hits = pygame.sprite.spritecollide(player, enemies, True)
    for hit in hits:
        explosion_sound.play()
        player.lives -= 1
        enemy = Enemy()
        all_sprites.add(enemy)
        enemies.add(enemy)
        if player.lives <= 0:
            show_game_over_screen()
            player.lives = 3  # Reset lives
            score = 0  # Reset score

    # Check for enemy bullets hitting player
    hits = pygame.sprite.spritecollide(player, enemy_bullets, True)
    for hit in hits:
        explosion_sound.play()
        player.lives -= 1
        if player.lives <= 0:
            show_game_over_screen()
            player.lives = 3  # Reset lives
            score = 0  # Reset score

    # Spawn new enemies gradually
    if len(enemies) < 5:  # Reduced enemy spawn rate
        new_enemy = Enemy()
        all_sprites.add(new_enemy)
        enemies.add(new_enemy)

    # Render
    screen.fill(BLACK)
    try:
        frame = next(background_frame_iter)
        frame_surface = pygame.surfarray.make_surface(frame)
        frame_surface = pygame.transform.scale(frame_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.blit(frame_surface, (0, 0))
    except StopIteration:
        background_frame_iter = iter(background_frames)
        frame = next(background_frame_iter)
        frame_surface = pygame.surfarray.make_surface(frame)
        frame_surface = pygame.transform.scale(frame_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.blit(frame_surface, (0, 0))

    all_sprites.draw(screen)
    draw_text(screen, "Score: " + str(score), 18, SCREEN_WIDTH // 2, 10)
    draw_text(screen, "Lives: " + str(player.lives), 18, SCREEN_WIDTH - 80, 10)

    pygame.display.flip()

pygame.quit()
