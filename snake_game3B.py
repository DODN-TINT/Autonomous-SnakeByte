import pygame
import random
import sys
from collections import deque

# === Configuration Constants ===
CELL_SIZE    = 20
GRID_WIDTH   = 20
GRID_HEIGHT  = 20
WINDOW_WIDTH = CELL_SIZE * GRID_WIDTH
WINDOW_HEIGHT = CELL_SIZE * GRID_HEIGHT
FPS = 10  # Frames per second

# Colors (R, G, B)
WHITE  = (255, 255, 255)
BLACK  = (0, 0, 0)
GREEN  = (0, 255, 0)       # Snake color
PURPLE = (128, 0, 128)     # Trap color

# Candidate apple colors (avoid GREEN, PURPLE, WHITE, BLACK)
APPLE_COLORS = [
    (255, 0, 0),       # Red
    (255, 165, 0),     # Orange
    (255, 255, 0),     # Yellow
    (0, 0, 255),       # Blue
    (0, 255, 255),     # Cyan
    (255, 0, 255)      # Magenta
]

# Directions (dx, dy)
UP    = (0, -1)
DOWN  = (0,  1)
LEFT  = (-1, 0)
RIGHT = (1,  0)

# === Helper Functions ===

def get_random_free_position(occupied):
    """
    Return a random grid cell (x, y) that is not in the occupied set.
    """
    while True:
        pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
        if pos not in occupied:
            return pos

def bfs(start, target, snake, traps):
    """
    Uses Breadth-First Search (BFS) to find a path from start to target.
    The snake’s body (all segments, including the tail) and traps are considered obstacles.
    
    Returns:
        A list of grid positions (cells) representing the shortest path from start
        to target (excluding the start cell). Returns None if no path is found.
    """
    obstacles = set(snake) | set(traps)
    queue = deque([start])
    came_from = {start: None}

    while queue:
        current = queue.popleft()
        if current == target:
            # Reconstruct the path from target back to start.
            path = []
            while current != start:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path

        for d in [UP, DOWN, LEFT, RIGHT]:
            next_cell = (current[0] + d[0], current[1] + d[1])
            if (0 <= next_cell[0] < GRID_WIDTH and
                0 <= next_cell[1] < GRID_HEIGHT and
                next_cell not in came_from and
                next_cell not in obstacles):
                came_from[next_cell] = current
                queue.append(next_cell)
    return None

def get_direction(from_cell, to_cell):
    """
    Return the (dx, dy) direction from from_cell to an adjacent to_cell.
    """
    return (to_cell[0] - from_cell[0], to_cell[1] - from_cell[1])

def draw_grid(surface):
    """
    Draw grid lines on the surface for visual effect.
    """
    for x in range(0, WINDOW_WIDTH, CELL_SIZE):
        pygame.draw.line(surface, WHITE, (x, 0), (x, WINDOW_HEIGHT))
    for y in range(0, WINDOW_HEIGHT, CELL_SIZE):
        pygame.draw.line(surface, WHITE, (0, y), (WINDOW_WIDTH, y))

def play_crash_sound(crash_sound):
    """
    Plays the crash sound 2-3 times consecutively with a short delay.
    """
    if crash_sound:
        times = random.randint(2, 3)
        for _ in range(times):
            crash_sound.play()
            # Delay to allow the sound to finish (adjust as needed)
            pygame.time.wait(300)

# === Main Game Loop ===

def main():
    pygame.init()
    pygame.mixer.init()

      # Load sounds.
    try:
        chirp_sound = pygame.mixer.Sound("chirp.wav")
    except pygame.error:
        print("Could not load chirp.wav. Please ensure it is in the same folder as this script.")
        chirp_sound = None

    try:
        crash_sound = pygame.mixer.Sound("crash.wav")
    except pygame.error:
        print("Could not load crash.wav. Please ensure it is in the same folder as this script.")
        crash_sound = None

    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("AI Snake Game with Traps, Scoring & Random Apple Colors")
    clock = pygame.time.Clock()

    # Initialize score and font.
    score = 0
    font = pygame.font.SysFont("Arial", 24)

    # Initialize snake: starting with 3 segments.
    snake = [
        (GRID_WIDTH // 2, GRID_HEIGHT // 2),
        (GRID_WIDTH // 2 - 1, GRID_HEIGHT // 2),
        (GRID_WIDTH // 2 - 2, GRID_HEIGHT // 2)
    ]
    direction = RIGHT

    # Initialize traps list (each trap is a grid cell that remains on the board)
    traps = []
    last_trap_time = pygame.time.get_ticks()

    # Place the first apple (avoid snake and traps)
    occupied_for_fruit = set(snake) | set(traps)
    fruit_pos = get_random_free_position(occupied_for_fruit)
    fruit_color = random.choice(APPLE_COLORS)

    running = True
    while running:
        clock.tick(FPS)
        current_time = pygame.time.get_ticks()

        # Add a new trap every 1 second.
        if current_time - last_trap_time >= 1000:
            occupied_for_trap = set(snake) | set(traps) | {fruit_pos}
            new_trap = get_random_free_position(occupied_for_trap)
            traps.append(new_trap)
            last_trap_time = current_time

        # Process events.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

         # AI usinBFS Algorithm
        # Prioritize following a direct path to the apple.
        path_to_fruit = bfs(snake[0], fruit_pos, snake, traps)
        if path_to_fruit is not None:
            next_cell = path_to_fruit[0]
            direction = get_direction(snake[0], next_cell)
        else:
            # If no direct path exists, try following the tail.
            path_to_tail = bfs(snake[0], snake[-1], snake, traps)
            if path_to_tail is not None:
                next_cell = path_to_tail[0]
                direction = get_direction(snake[0], next_cell)
            else:
                # As a last resort, choose any valid move.
                for d in [UP, DOWN, LEFT, RIGHT]:
                    next_cell = (snake[0][0] + d[0], snake[0][1] + d[1])
                    if (0 <= next_cell[0] < GRID_WIDTH and
                        0 <= next_cell[1] < GRID_HEIGHT and
                        next_cell not in snake and
                        next_cell not in traps):
                        direction = d
                        break

        # ===== MOVE THE SNAKE =====
        new_head = (snake[0][0] + direction[0], snake[0][1] + direction[1])

        # Check for collisions with walls or the snake's body (including tail).
        if (new_head[0] < 0 or new_head[0] >= GRID_WIDTH or
            new_head[1] < 0 or new_head[1] >= GRID_HEIGHT or
            new_head in snake):
            play_crash_sound(crash_sound)
            print("Game over! Final score:", score)
            running = False
            continue

        # If the snake hits a trap, play crash sound, then cut its length to half.
        elif new_head in traps:
            play_crash_sound(crash_sound)
            snake.insert(0, new_head)
            new_length = max(1, len(snake) // 2)
            snake = snake[:new_length]
            print("Hit trap! Snake length cut to half. New length:", len(snake))
        
        # If the snake eats the apple.
        elif new_head == fruit_pos:
            snake.insert(0, new_head)
            if chirp_sound:
                chirp_sound.play()
            # Increase score based on snake length and number of traps.
            # (The harder it is, the higher the reward.)
            apple_reward = 10 + len(snake) + len(traps)
            score += apple_reward
            print("Apple eaten! Score increased by", apple_reward, "New score:", score)
            # Place a new apple (avoid snake and traps), with a random color.
            occupied_for_fruit = set(snake) | set(traps)
            fruit_pos = get_random_free_position(occupied_for_fruit)
            fruit_color = random.choice(APPLE_COLORS)
        else:
            # Normal move.
            snake.insert(0, new_head)
            snake.pop()

        # ===== DRAWING =====
        screen.fill(BLACK)
        # Draw the apple.
        pygame.draw.rect(screen, fruit_color, (fruit_pos[0] * CELL_SIZE, fruit_pos[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        # Draw the traps.
        for trap in traps:
            pygame.draw.rect(screen, PURPLE, (trap[0] * CELL_SIZE, trap[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        # Draw the snake.
        for segment in snake:
            pygame.draw.rect(screen, GREEN, (segment[0] * CELL_SIZE, segment[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        # Draw grid lines.
        draw_grid(screen)
        # Draw the score.
        score_text = font.render("Score: " + str(score), True, WHITE)
        screen.blit(score_text, (10, 10))
        pygame.display.update()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
