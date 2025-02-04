import pygame
import random
import sys
import numpy as np
from stable_baselines3 import DQN  # Used to load the trained model

# === Configuration Constants ===
CELL_SIZE    = 20
GRID_WIDTH   = 20
GRID_HEIGHT  = 20
WINDOW_WIDTH = CELL_SIZE * GRID_WIDTH
WINDOW_HEIGHT = CELL_SIZE * GRID_HEIGHT
FPS = 10  # Frames per second

# Colors (RGB)
BLACK  = (0, 0, 0)
WHITE  = (255, 255, 255)
GREEN  = (0, 255, 0)       # Snake color
PURPLE = (128, 0, 128)     # Trap color

# Candidate apple colors (avoid conflicts with snake/traps/black/white)
APPLE_COLORS = [
    (255, 0, 0),       # Red
    (255, 165, 0),     # Orange
    (255, 255, 0),     # Yellow
    (0, 0, 255),       # Blue
    (0, 255, 255),     # Cyan
    (255, 0, 255)      # Magenta
]

# Mapping from discrete actions to movement directions.
# 0: UP, 1: DOWN, 2: LEFT, 3: RIGHT
ACTION_TO_DIRECTION = {
    0: (0, -1),
    1: (0, 1),
    2: (-1, 0),
    3: (1, 0)
}

# Dictionary to get the opposite direction for prevention of reversal.
OPPOSITE_DIRECTION = {
    (0, -1): (0, 1),
    (0, 1): (0, -1),
    (-1, 0): (1, 0),
    (1, 0): (-1, 0)
}

# === Helper Functions ===

def get_random_free_position(occupied):
    """Return a random (x, y) position on the grid that is not occupied."""
    while True:
        pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
        if pos not in occupied:
            return pos

def get_observation(snake, apple, traps):
    """
    Create a grid-based observation as a 2D NumPy array.
      0 = empty, 1 = snake, 2 = apple, 3 = trap.
    """
    obs = np.zeros((GRID_HEIGHT, GRID_WIDTH), dtype=np.int8)
    for (x, y) in snake:
        obs[y, x] = 1
    ax, ay = apple
    obs[ay, ax] = 2
    for (x, y) in traps:
        obs[y, x] = 3
    return obs

def draw_grid(surface):
    """Draw grid lines on the provided surface."""
    for x in range(0, WINDOW_WIDTH, CELL_SIZE):
        pygame.draw.line(surface, WHITE, (x, 0), (x, WINDOW_HEIGHT))
    for y in range(0, WINDOW_HEIGHT, CELL_SIZE):
        pygame.draw.line(surface, WHITE, (0, y), (WINDOW_WIDTH, y))

def play_crash_sound(crash_sound):
    """
    Play the crash sound 2–3 times consecutively with a short delay between plays.
    """
    if crash_sound:
        times = random.randint(2, 3)
        for _ in range(times):
            crash_sound.play()
            pygame.time.wait(300)

# === Main Game Function ===

def main():
    pygame.init()
    pygame.mixer.init()

    # Load sounds.
    try:
        chirp_sound = pygame.mixer.Sound("chirp.wav")
    except pygame.error:
        print("Could not load chirp.wav. Please ensure it is in the same folder.")
        chirp_sound = None

    try:
        crash_sound = pygame.mixer.Sound("crash.wav")
    except pygame.error:
        print("Could not load crash.wav. Please ensure it is in the same folder.")
        crash_sound = None

    # Load the pre-trained DQN model.
    try:
        model = DQN.load("dqn_snake_model")
        print("DQN model loaded successfully.")
    except Exception as e:
        print("Error loading DQN model:", e)
        model = None

    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("AI Snake Game with DQN")
    clock = pygame.time.Clock()

    # Initialize snake: start with 3 segments.
    snake = [
        (GRID_WIDTH // 2, GRID_HEIGHT // 2),
        (GRID_WIDTH // 2 - 1, GRID_HEIGHT // 2),
        (GRID_WIDTH // 2 - 2, GRID_HEIGHT // 2)
    ]
    current_direction = (1, 0)  # Initially moving right.

    # Place the first apple.
    occupied = set(snake)
    apple = get_random_free_position(occupied)
    apple_color = random.choice(APPLE_COLORS)

    # Initialize traps.
    traps = []
    trap_interval = 1000  # Add one trap every 1000 ms (1 second).
    last_trap_time = pygame.time.get_ticks()

    score = 0
    running = True

    while running:
        clock.tick(FPS)
        current_time = pygame.time.get_ticks()

        # Process events.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Add a new trap every second.
        if current_time - last_trap_time >= trap_interval:
            occupied_for_trap = set(snake) | set(traps) | {apple}
            new_trap = get_random_free_position(occupied_for_trap)
            traps.append(new_trap)
            last_trap_time = current_time

        # --- AI Decision Making using DQN ---
        obs = get_observation(snake, apple, traps)
        # Expand dimensions to add batch dimension (model expects shape: (1, height, width)).
        if model is not None:
            action, _ = model.predict(obs[None, ...], deterministic=True)
            action = int(action)
        else:
            # Fallback: choose a random valid action.
            action = random.choice([0, 1, 2, 3])
        new_direction = ACTION_TO_DIRECTION[action]

        # Prevent immediate reversal if the snake has more than one segment.
        if len(snake) > 1 and new_direction == OPPOSITE_DIRECTION[current_direction]:
            new_direction = current_direction
        current_direction = new_direction

        # --- Move the Snake ---
        head_x, head_y = snake[0]
        dx, dy = current_direction
        new_head = (head_x + dx, head_y + dy)

        # Check for collision with walls.
        if (new_head[0] < 0 or new_head[0] >= GRID_WIDTH or
            new_head[1] < 0 or new_head[1] >= GRID_HEIGHT):
            play_crash_sound(crash_sound)
            print("Game over! Final score:", score)
            running = False
            continue

        # Check for collision with itself.
        if new_head in snake:
            play_crash_sound(crash_sound)
            print("Game over! Final score:", score)
            running = False
            continue

        # If the snake eats the apple.
        if new_head == apple:
            snake.insert(0, new_head)  # Grow the snake.
            apple_reward = 10 + len(snake) + len(traps)
            score += apple_reward
            if chirp_sound:
                chirp_sound.play()
            # Place a new apple (avoid snake and traps) with a random color.
            occupied = set(snake) | set(traps)
            apple = get_random_free_position(occupied)
            apple_color = random.choice(APPLE_COLORS)
        # If the snake hits a trap.
        elif new_head in traps:
            snake.insert(0, new_head)
            new_length = max(1, len(snake) // 2)
            snake = snake[:new_length]
            score -= 10
            play_crash_sound(crash_sound)
        else:
            # Normal move: add new head and remove tail.
            snake.insert(0, new_head)
            snake.pop()

        # --- Rendering ---
        screen.fill(BLACK)
        draw_grid(screen)
        # Draw the apple.
        ax, ay = apple
        pygame.draw.rect(screen, apple_color, (ax * CELL_SIZE, ay * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        # Draw traps.
        for (tx, ty) in traps:
            pygame.draw.rect(screen, PURPLE, (tx * CELL_SIZE, ty * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        # Draw the snake.
        for (sx, sy) in snake:
            pygame.draw.rect(screen, GREEN, (sx * CELL_SIZE, sy * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        # Draw the score.
        font = pygame.font.SysFont("Arial", 24)
        score_text = font.render("Score: " + str(score), True, WHITE)
        screen.blit(score_text, (10, 10))
        pygame.display.update()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
