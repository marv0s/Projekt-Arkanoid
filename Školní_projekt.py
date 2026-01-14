import pygame
import random

# Inicializace pygame
pygame.init()

# Konstanty
WIDTH, HEIGHT = 1000, 700
BALL_SPEED = 6
PADDLE_SPEED = 10
BLOCK_ROWS, BLOCK_COLS = 6, 10
BLOCK_WIDTH, BLOCK_HEIGHT = WIDTH // BLOCK_COLS, 40
LIVES = 3
BALL_SIZE = 20

# Barvy
WHITE = (255, 255, 255)
RED = (255, 0, 0)
PADDLE_COLOR = (50, 50, 200)
SPECIAL_BLOCK_COLOR = (255, 215, 0)
UNBREAKABLE_BLOCK_COLOR = (128, 128, 128)
BACKGROUND_COLOR = (30, 30, 30)

# Nastavení okna
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Arkanoid")
font = pygame.font.Font(None, 36)

# Funkce pro vytvoření bloků (nezničitelné bloky nesmí být vedle sebe nebo pod sebou)
def create_blocks():
    blocks = []
    unbreakable_map = [[False for _ in range(BLOCK_COLS)] for _ in range(BLOCK_ROWS)]

    for row in range(BLOCK_ROWS):
        last_was_unbreakable = False
        for col in range(BLOCK_COLS):
            rect = pygame.Rect(col * BLOCK_WIDTH, row * BLOCK_HEIGHT, BLOCK_WIDTH, BLOCK_HEIGHT)
            rand_val = random.random()
            above_unbreakable = unbreakable_map[row - 1][col] if row > 0 else False

            if last_was_unbreakable or above_unbreakable:
                if rand_val < 0.3:
                    color = SPECIAL_BLOCK_COLOR
                    block_type = "special"
                else:
                    color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
                    block_type = "normal"
                last_was_unbreakable = False
                unbreakable_map[row][col] = False
            else:
                if rand_val < 0.2:
                    color = UNBREAKABLE_BLOCK_COLOR
                    block_type = "unbreakable"
                    last_was_unbreakable = True
                    unbreakable_map[row][col] = True
                elif rand_val < 0.3:
                    color = SPECIAL_BLOCK_COLOR
                    block_type = "special"
                    last_was_unbreakable = False
                    unbreakable_map[row][col] = False
                else:
                    color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
                    block_type = "normal"
                    last_was_unbreakable = False
                    unbreakable_map[row][col] = False

            blocks.append((rect, color, block_type))
    return blocks

# Restart hry
def reset_game():
    global ball, ball_dx, ball_dy, blocks, score, lives
    paddle.x = WIDTH // 2 - 75
    ball.x, ball.y = WIDTH // 2 - BALL_SIZE//2, HEIGHT // 2
    ball_dx, ball_dy = BALL_SPEED, -BALL_SPEED
    blocks = create_blocks()
    score = 0
    lives = LIVES

# Funkce pro vyřešení kolize míčku s blokem
def resolve_block_collision(ball, block, dx, dy):
    overlap_left = ball.right - block.left
    overlap_right = block.right - ball.left
    overlap_top = ball.bottom - block.top
    overlap_bottom = block.bottom - ball.top

    min_overlap_x = min(overlap_left, overlap_right)
    min_overlap_y = min(overlap_top, overlap_bottom)

    if min_overlap_x < min_overlap_y:
        # horizontální odraz
        if overlap_left < overlap_right:
            ball.right = block.left
        else:
            ball.left = block.right
        dx = -dx
    else:
        # vertikální odraz
        if overlap_top < overlap_bottom:
            ball.bottom = block.top
        else:
            ball.top = block.bottom
        dy = -dy

    return dx, dy

# Pálka a míček
paddle = pygame.Rect(WIDTH // 2 - 75, HEIGHT - 30, 150, 15)
ball = pygame.Rect(WIDTH // 2 - BALL_SIZE//2, HEIGHT // 2, BALL_SIZE, BALL_SIZE)
ball_dx, ball_dy = BALL_SPEED, -BALL_SPEED
blocks = create_blocks()
score = 0
lives = LIVES
paused = False

# Pauza
def toggle_pause():
    global paused
    paused = not paused
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                paused = False

# Hlavní smyčka
running = True
clock = pygame.time.Clock()
while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
            toggle_pause()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and paddle.left > 0:
        paddle.x -= PADDLE_SPEED
    if keys[pygame.K_RIGHT] and paddle.right < WIDTH:
        paddle.x += PADDLE_SPEED

    # Uložit předchozí pozici míčku
    prev_x, prev_y = ball.x, ball.y

    # Pohyb míčku
    ball.x += ball_dx
    ball.y += ball_dy

    # Kolize se stěnami – přesné zamezení prolétnutí
    if ball.left <= 0:
        ball.left = 0
        ball_dx = -ball_dx
    if ball.right >= WIDTH:
        ball.right = WIDTH
        ball_dx = -ball_dx
    if ball.top <= 0:
        ball.top = 0
        ball_dy = -ball_dy

    # Kolize s pálkou
    if ball.colliderect(paddle):
        ball.bottom = paddle.top
        offset = (ball.centerx - paddle.centerx) / (paddle.width / 2)
        ball_dx = BALL_SPEED * offset
        ball_dy = -BALL_SPEED

    # Kolize s bloky
    for block, color, block_type in blocks[:]:
        if ball.colliderect(block):
            if block_type != "unbreakable":
                blocks.remove((block, color, block_type))
                score += 50 if block_type == "special" else 10
            ball_dx, ball_dy = resolve_block_collision(ball, block, ball_dx, ball_dy)
            break

    # Prohra
    if ball.bottom >= HEIGHT:
        lives -= 1
        if lives == 0:
            pygame.time.delay(2000)
            reset_game()
        else:
            ball.x, ball.y = WIDTH // 2 - BALL_SIZE//2, HEIGHT // 2
            ball_dx, ball_dy = BALL_SPEED, -BALL_SPEED

    # Vykreslení
    screen.fill(BACKGROUND_COLOR)
    pygame.draw.rect(screen, PADDLE_COLOR, paddle, border_radius=5)
    pygame.draw.ellipse(screen, RED, ball)
    for block, color, block_type in blocks:
        pygame.draw.rect(screen, color, block, border_radius=5)

    score_text = font.render(f"Skóre: {score}  Životy: {lives}", True, WHITE)
    screen.blit(score_text, (10, 10))

    pygame.display.update()

pygame.quit()
