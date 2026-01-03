import pygame
import random

# =========================
# Inisialisasi Pygame
# =========================
pygame.init()
pygame.mixer.init()

# =========================
# Konstanta
# =========================
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GRAVITY = 1

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# =========================
# Setup layar
# =========================
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Boxing Game 1 vs 1")
clock = pygame.time.Clock()

# =========================
# Load Background
# =========================
try:
    background = pygame.image.load("background_arena.jpeg").convert()
    background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
except:
    background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    background.fill((120, 120, 120))

# =========================
# Load Sound
# =========================
try:
    cheer_sound = pygame.mixer.Sound("crowd-cheering-in-stadium-435357.mp3")
    punch_sound = pygame.mixer.Sound("punch_h_05-224063.mp3")
    jump_sound = pygame.mixer.Sound("fast-simple-chop.mp3")
    bell_sound = pygame.mixer.Sound("opening-bell-421471.mp3")
except:
    cheer_sound = punch_sound = jump_sound = bell_sound = None

# =========================
# Kelas Boxer
# =========================
class Boxer(pygame.sprite.Sprite):
    def __init__(self, x, y, image_path, controls):
        super().__init__()

        # Load image
        try:
            self.image = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (80, 120))
        except:
            self.image = pygame.Surface((80, 120))
            self.image.fill((200, 0, 0))

        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

        self.speed = 5
        self.health = 100
        self.controls = controls

        # Punch
        self.punching = False
        self.punch_timer = 0
        self.arm_length = 0
        self.facing = 1

        # Jump / gravity
        self.vel_y = 0
        self.on_ground = True

        # Knockback
        self.knockback_vel = 0

    def update(self):
        keys = pygame.key.get_pressed()

        # ===== Gerakan Kiri / Kanan =====
        if keys[self.controls['left']]:
            self.rect.x -= self.speed
            self.facing = -1
        if keys[self.controls['right']]:
            self.rect.x += self.speed
            self.facing = 1

        # ===== Jump =====
        if keys[self.controls['jump']] and self.on_ground:
            self.vel_y = -18
            self.on_ground = False
            if jump_sound:
                jump_sound.play()

        # ===== Gravitasi =====
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y
        if self.rect.bottom >= 520:
            self.rect.bottom = 520
            self.vel_y = 0
            self.on_ground = True

        # ===== Punch =====
        if keys[self.controls['punch']] and not self.punching:
            self.punching = True
            self.punch_timer = 10
            self.arm_length = 40
            if punch_sound:
                punch_sound.play()
            if cheer_sound:
                cheer_sound.play()

        if self.punching:
            self.punch_timer -= 1
            self.arm_length -= 4
            if self.punch_timer <= 0:
                self.punching = False
                self.arm_length = 0

        # ===== Knockback =====
        if self.knockback_vel != 0:
            self.rect.x += self.knockback_vel
            self.knockback_vel *= 0.8
            if abs(self.knockback_vel) < 0.5:
                self.knockback_vel = 0

        # ===== Batas Arena =====
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

    def draw(self, screen):
        screen.blit(self.image, self.rect)

        # ===== Arm / Punch =====
        if self.punching:
            shoulder_x = self.rect.centerx + (20 * self.facing)
            shoulder_y = self.rect.centery - 10
            fist_x = shoulder_x + (self.arm_length * self.facing)
            fist_y = shoulder_y

            pygame.draw.line(screen, (255, 220, 180), (shoulder_x, shoulder_y), (fist_x, fist_y), 6)
            pygame.draw.circle(screen, (200, 180, 150), (int(fist_x), int(fist_y)), 8)

        # ===== Health Bar =====
        pygame.draw.rect(screen, BLACK, (self.rect.x, self.rect.y - 15, 80, 10))
        pygame.draw.rect(screen, (0, 255, 0), (self.rect.x, self.rect.y - 15, self.health * 0.8, 10))


# =========================
# Player
# =========================
player1 = Boxer(200, 420, "petinju1.jpg", {'left': pygame.K_a, 'right': pygame.K_d, 'jump': pygame.K_SPACE, 'punch': pygame.K_w})
player2 = Boxer(600, 420, "petinju2.jpg", {'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 'jump': pygame.K_KP0, 'punch': pygame.K_UP})

all_sprites = pygame.sprite.Group(player1, player2)

# =========================
# Game Timer
# =========================
ROUND_TIME = 60
start_ticks = pygame.time.get_ticks()
game_over = False
winner_text = ""
font = pygame.font.SysFont("arial", 40)

# =========================
# Loop Game
# =========================
running = True
while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # ===== Update =====
    if not game_over:
        all_sprites.update()

        # ===== Deteksi Pukulan & Knockback =====
        if player1.punching and player1.rect.colliderect(player2.rect) and player2.knockback_vel == 0:
            player2.health -= 5
            player2.knockback_vel = 8 * player1.facing

        if player2.punching and player2.rect.colliderect(player1.rect) and player1.knockback_vel == 0:
            player1.health -= 5
            player1.knockback_vel = 8 * player2.facing

        # ===== Cegah Tembus =====
        if player1.rect.colliderect(player2.rect):
            if player1.knockback_vel > 0: player1.knockback_vel = 0
            if player2.knockback_vel < 0: player2.knockback_vel = 0

        # ===== Cek Pemenang =====
        if player1.health <= 0:
            winner_text = "PLAYER 2 WINS!"
            game_over = True
            if bell_sound: bell_sound.play()
        elif player2.health <= 0:
            winner_text = "PLAYER 1 WINS!"
            game_over = True
            if bell_sound: bell_sound.play()

    # ===== Timer =====
    seconds_passed = (pygame.time.get_ticks() - start_ticks) // 1000
    time_left = max(0, ROUND_TIME - seconds_passed)
    if time_left == 0 and not game_over:
        game_over = True
        if bell_sound: bell_sound.play()
        if player1.health > player2.health:
            winner_text = "PLAYER 1 WINS!"
        elif player2.health > player1.health:
            winner_text = "PLAYER 2 WINS!"
        else:
            winner_text = "DRAW!"

    # ===== Render =====
    screen.blit(background, (0, 0))
    for sprite in all_sprites:
        sprite.draw(screen)

    timer_text = font.render(f"TIME: {time_left}", True, WHITE)
    screen.blit(timer_text, (SCREEN_WIDTH // 2 - 70, 20))

    # ===== Game Over Overlay =====
    if game_over:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0,0,0))
        screen.blit(overlay, (0,0))
        screen.blit(font.render("GAME OVER", True, (255,0,0)), (SCREEN_WIDTH//2-120, 250))
        screen.blit(font.render(winner_text, True, WHITE), (SCREEN_WIDTH//2-160, 300))

    pygame.display.flip()

pygame.quit()
