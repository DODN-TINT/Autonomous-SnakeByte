import pygame
import random
import sys
from collections import deque

# === Configuration constants ===
CELL_SIZE   = 20
GRID_WIDTH  = 20
GRID_HEIGHT = 20
WINDOW_WIDTH  = CELL_SIZE * GRID_WIDTH
WINDOW_HEIGHT = CELL_SIZE * GRID_HEIGHT
FPS = 10

# Colors (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED   = (255, 0, 0)

# Directions (dx, dy)
UP    = (0, -1)
DOWN  = (0,  1)
LEFT  = (-1, 0)
RIGHT = (1,  0)

# === Helper functions ===

def get_random_position(snake):
    """Return a random grid cell that is not occupied by the snake."""
    while True:
        pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
        if pos not in snake:
            return pos

def bfs(start, target, snake, allow_tail_as_free=False):
    """
    Use breadth-first search (BFS) to find a path from start to target.
    The snake’s body cells are treated as obstacles.
    If allow_tail_as_free is True then the tail cell is considered free (since it will move).
    
    Returns:
        A list of grid positions (cells) that is the shortest path from start to target,
        not including the start cell. Returns None if no path is found.
    """
    obstacles = set(snake)
    if allow_tail_as_free and snake:
        # The tail will move; so temporarily remove it as an obstacle.
        obstacles.remove(snake[-1])
    
    queue = deque()
    queue.append(start)
    came_from = {start: None}

    while queue:
        current = queue.popleft()
        if current == target:
            # Reconstruct the path by walking backwards from target to start.
            path = []
            while current != start:
                path.append(current)
                current = came_from[current]
            path.reverse()  # so that the first step is first
            return path
        # Check all four neighbors
        for direction in [UP, DOWN, LEFT, RIGHT]:
            next_cell = (current[0] + direction[0], current[1] + direction[1])
            # Make sure next_cell is within bounds and not an obstacle.
            if (0 <= next_cell[0] < GRID_WIDTH and 
                0 <= next_cell[1] < GRID_HEIGHT and 
                next_cell not in came_from and 
                next_cell not in obstacles):
                came_from[next_cell] = current
                queue.append(next_cell)
    return None

def get_direction(from_cell, to_cell):
    """Given two adjacent cells, return the direction as a (dx,dy) tuple."""
    return (to_cell[0] - from_cell[0], to_cell[1] - from_cell[1])

def draw_grid(surface):
    """Draw a grid on the given surface (for visual effect)."""
    for x in range(0, WINDOW_WIDTH, CELL_SIZE):
        pygame.draw.line(surface, WHITE, (x, 0), (x, WINDOW_HEIGHT))
    for y in range(0, WINDOW_HEIGHT, CELL_SIZE):
        pygame.draw.line(surface, WHITE, (0, y), (WINDOW_WIDTH, y))

# === Main game loop ===

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("AI Snake Game")
    clock = pygame.time.Clock()

    # Initialize snake: start with a length of 3 segments.
    snake = [
        (GRID_WIDTH // 2, GRID_HEIGHT // 2),
        (GRID_WIDTH // 2 - 1, GRID_HEIGHT // 2),
        (GRID_WIDTH // 2 - 2, GRID_HEIGHT // 2)
    ]
    direction = RIGHT

    # Place the first fruit
    fruit = get_random_position(snake)

    running = True
    while running:
        clock.tick(FPS)

        # Handle quit events.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # ===== AI DECISION MAKING =====
        # First, try to find a path from the snake's head to the fruit.
        path_to_fruit = bfs(snake[0], fruit, snake, allow_tail_as_free=True)
        if path_to_fruit is not None:
            # Simulate following the path to check safety:
            simulated_snake = snake.copy()
            for cell in path_to_fruit:
                # Add the new head.
                simulated_snake.insert(0, cell)
                if cell == fruit:
                    # If fruit is eaten, the snake grows (do not remove tail).
                    pass
                else:
                    # Otherwise, remove the tail.
                    simulated_snake.pop()
            # Now check: can the simulated snake reach its own tail?
            safe = bfs(simulated_snake[0], simulated_snake[-1], simulated_snake, allow_tail_as_free=True) is not None
            if safe:
                # Follow the first step along the path to fruit.
                next_cell = path_to_fruit[0]
                direction = get_direction(snake[0], next_cell)
            else:
                # If following the fruit path is not “safe,” try to follow the tail.
                path_to_tail = bfs(snake[0], snake[-1], snake, allow_tail_as_free=True)
                if path_to_tail is not None:
                    next_cell = path_to_tail[0]
                    direction = get_direction(snake[0], next_cell)
                else:
                    # If even that fails, pick any valid move.
                    for d in [UP, DOWN, LEFT, RIGHT]:
                        next_cell = (snake[0][0] + d[0], snake[0][1] + d[1])
                        if (0 <= next_cell[0] < GRID_WIDTH and
                            0 <= next_cell[1] < GRID_HEIGHT and 
                            next_cell not in snake):
                            direction = d
                            break
        else:
            # No direct path to the fruit.
            # Try moving toward the tail (which is always safe if available).
            path_to_tail = bfs(snake[0], snake[-1], snake, allow_tail_as_free=True)
            if path_to_tail is not None:
                next_cell = path_to_tail[0]
                direction = get_direction(snake[0], next_cell)
            else:
                # If no safe option is found, pick any valid direction.
                for d in [UP, DOWN, LEFT, RIGHT]:
                    next_cell = (snake[0][0] + d[0], snake[0][1] + d[1])
                    if (0 <= next_cell[0] < GRID_WIDTH and
                        0 <= next_cell[1] < GRID_HEIGHT and 
                        next_cell not in snake):
                        direction = d
                        break

        # ===== MOVE THE SNAKE =====
        new_head = (snake[0][0] + direction[0], snake[0][1] + direction[1])
        # Check for collisions with walls or itself.
        if (new_head[0] < 0 or new_head[0] >= GRID_WIDTH or
            new_head[1] < 0 or new_head[1] >= GRID_HEIGHT or
            new_head in snake):
            print("Game over! Final score:", len(snake))
            running = False
            continue

        # If the snake has eaten the fruit:
        if new_head == fruit:
            snake.insert(0, new_head)
            fruit = get_random_position(snake)
        else:
            # Normal move: add new head and remove tail.
            snake.insert(0, new_head)
            snake.pop()

        # ===== DRAWING =====
        screen.fill(BLACK)
        # Draw the fruit.
        pygame.draw.rect(screen, RED, (fruit[0] * CELL_SIZE, fruit[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))
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
