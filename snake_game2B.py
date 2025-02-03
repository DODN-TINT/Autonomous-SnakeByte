import pygame
import random
import sys
from collections import deque

# === Configuration constants ===
CELL_SIZE    = 20
GRID_WIDTH   = 20
GRID_HEIGHT  = 20
WINDOW_WIDTH = CELL_SIZE * GRID_WIDTH
WINDOW_HEIGHT = CELL_SIZE * GRID_HEIGHT
FPS = 10  # Frames per second

# Colors (R, G, B)
WHITE  = (255, 255, 255)
BLACK  = (0, 0, 0)
GREEN  = (0, 255, 0)
RED    = (255, 0, 0)
PURPLE = (128, 0, 128)

# Directions (dx, dy)
UP    = (0, -1)
DOWN  = (0,  1)
LEFT  = (-1, 0)
RIGHT = (1,  0)

# === Helper functions ===

def get_random_free_position(occupied):
    """Return a random grid cell that is not in the occupied set."""
    while True:
        pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
        if pos not in occupied:
            return pos

def bfs(start, target, snake, traps):
    """
    Use breadth-first search (BFS) to find a path from start to target.
    The snake's body (including its tail) and traps are treated as obstacles.
    
    Returns:
        A list of grid positions (cells) that is the shortest path from start 
        to target (not including the start cell). Returns None if no path is found.
    """
    obstacles = set(snake) | set(traps)
    queue = deque()
    queue.append(start)
    came_from = {start: None}

    while queue:
        current = queue.popleft()
        if current == target:
            # Reconstruct path by working backward from target to start.
            path = []
            while current != start:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path
        # Check all four neighbors
        for direction in [UP, DOWN, LEFT, RIGHT]:
            next_cell = (current[0] + direction[0], current[1] + direction[1])
            if (0 <= next_cell[0] < GRID_WIDTH and 
                0 <= next_cell[1] < GRID_HEIGHT and 
                next_cell not in came_from and 
                next_cell not in obstacles):
                came_from[next_cell] = current
                queue.append(next_cell)
    return None

def get_direction(from_cell, to_cell):
    """Return the (dx, dy) direction from from_cell to an adjacent to_cell."""
    return (to_cell[0] - from_cell[0], to_cell[1] - from_cell[1])

def draw_grid(surface):
    """Draw grid lines on the game window (for visual effect)."""
    for x in range(0, WINDOW_WIDTH, CELL_SIZE):
        pygame.draw.line(surface, WHITE, (x, 0), (x, WINDOW_HEIGHT))
    for y in range(0, WINDOW_HEIGHT, CELL_SIZE):
        pygame.draw.line(surface, WHITE, (0, y), (WINDOW_WIDTH, y))

# === Main game loop ===

def main():
    pygame.init()
    # Initialize the mixer for sound.
    pygame.mixer.init()
    try:
        chirp_sound = pygame.mixer.Sound("chirp.wav")
    except pygame.error:
        print("Could not load chirp.wav. Please ensure it is in the same folder as this script.")
        chirp_sound = None

    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("AI Snake Game with Traps")
    clock = pygame.time.Clock()

    # Initialize snake: start with 3 segments.
    snake = [
        (GRID_WIDTH // 2, GRID_HEIGHT // 2),
        (GRID_WIDTH // 2 - 1, GRID_HEIGHT // 2),
        (GRID_WIDTH // 2 - 2, GRID_HEIGHT // 2)
    ]
    direction = RIGHT

    # Initialize traps list (each trap is a grid cell that stays on the board)
    traps = []
    # We'll add one trap every 1000 ms (1 second).
    last_trap_time = pygame.time.get_ticks()

    # Place the first fruit (avoid snake and traps)
    occupied_for_fruit = set(snake) | set(traps)
    fruit = get_random_free_position(occupied_for_fruit)

    running = True
    while running:
        clock.tick(FPS)
        current_time = pygame.time.get_ticks()

        # Add a new trap every 1 second.
        if current_time - last_trap_time >= 1000:
            occupied_for_trap = set(snake) | set(traps) | {fruit}
            new_trap = get_random_free_position(occupied_for_trap)
            traps.append(new_trap)
            last_trap_time = current_time

        # Handle quit events.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # ===== AI DECISION MAKING =====
        # Try to find a path from the snake's head to the fruit.
        path_to_fruit = bfs(snake[0], fruit, snake, traps)
        if path_to_fruit is not None:
            # Simulate following the path to check safety:
            simulated_snake = snake.copy()
            for cell in path_to_fruit:
                simulated_snake.insert(0, cell)
                if cell == fruit:
                    # Fruit eaten, so snake grows (do not remove tail)
                    pass
                else:
                    simulated_snake.pop()
            # Check if after following the path, the snake's head can reach its tail.
            # (Under the new rules the tail is not considered free.)
            safe = bfs(simulated_snake[0], simulated_snake[-1], simulated_snake, traps) is not None
            if safe:
                next_cell = path_to_fruit[0]
                direction = get_direction(snake[0], next_cell)
            else:
                # Fallback: try following the tail.
                path_to_tail = bfs(snake[0], snake[-1], snake, traps)
                if path_to_tail is not None:
                    next_cell = path_to_tail[0]
                    direction = get_direction(snake[0], next_cell)
                else:
                    # If all else fails, pick any valid move.
                    for d in [UP, DOWN, LEFT, RIGHT]:
                        next_cell = (snake[0][0] + d[0], snake[0][1] + d[1])
                        if (0 <= next_cell[0] < GRID_WIDTH and
                            0 <= next_cell[1] < GRID_HEIGHT and 
                            next_cell not in snake and
                            next_cell not in traps):
                            direction = d
                            break
        else:
            # No path to the fruit found; try moving toward the tail.
            path_to_tail = bfs(snake[0], snake[-1], snake, traps)
            if path_to_tail is not None:
                next_cell = path_to_tail[0]
                direction = get_direction(snake[0], next_cell)
            else:
                # Pick any valid direction.
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
        
        # Check collisions with walls or the snake's own body (including tail).
        if (new_head[0] < 0 or new_head[0] >= GRID_WIDTH or
            new_head[1] < 0 or new_head[1] >= GRID_HEIGHT or
            new_head in snake):
            print("Game over! Final score:", len(snake))
            running = False
            continue

        # If the snake's head lands on a trap, cut its length to half.
        if new_head in traps:
            snake.insert(0, new_head)
            new_length = max(1, len(snake) // 2)
            snake = snake[:new_length]
            print("Hit trap! Snake length cut to half. New length:", len(snake))
        # If the snake eats the fruit:
        elif new_head == fruit:
            snake.insert(0, new_head)
            # Play the chirp sound if it loaded successfully.
            if chirp_sound:
                chirp_sound.play()
            # Place a new fruit (avoid snake and traps).
            occupied_for_fruit = set(snake) | set(traps)
            fruit = get_random_free_position(occupied_for_fruit)
        else:
            # Normal move: add new head and remove tail.
            snake.insert(0, new_head)
            snake.pop()

        # ===== DRAWING =====
        screen.fill(BLACK)
        # Draw the fruit.
        pygame.draw.rect(screen, RED, (fruit[0] * CELL_SIZE, fruit[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        # Draw the traps.
        for trap in traps:
            pygame.draw.rect(screen, PURPLE, (trap[0] * CELL_SIZE, trap[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        # Draw the snake.
        for segment in snake:
            pygame.draw.rect(screen, GREEN, (segment[0] * CELL_SIZE, segment[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        # Optionally, draw the grid lines.
        draw_grid(screen)
        pygame.display.update()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
