import gym
import numpy as np
import random
from gym import spaces
import pygame

# --- Global Constants ---
GRID_WIDTH = 20
GRID_HEIGHT = 20
CELL_SIZE = 20

# Colors (RGB)
COLOR_BG = (0, 0, 0)         # Black background
COLOR_GRID = (40, 40, 40)    # Dark gray grid lines
COLOR_SNAKE = (0, 255, 0)    # Green snake
COLOR_TRAP = (128, 0, 128)   # Purple traps
# Candidate apple colors (avoid green, purple, black, and grid color)
APPLE_COLORS = [
    (255, 0, 0),       # Red
    (255, 165, 0),     # Orange
    (255, 255, 0),     # Yellow
    (0, 0, 255),       # Blue
    (0, 255, 255),     # Cyan
    (255, 0, 255)      # Magenta
]

# Map actions to directions.
# 0: UP, 1: DOWN, 2: LEFT, 3: RIGHT
ACTION_TO_DIRECTION = {
    0: (0, -1),
    1: (0, 1),
    2: (-1, 0),
    3: (1, 0)
}

# Utility: Get the opposite action (to prevent immediate reversal)
OPPOSITE_ACTION = {0:1, 1:0, 2:3, 3:2}


# --- The Snake Environment ---
class SnakeEnv(gym.Env):
    """
    Gym environment for Snake.
    Observation:
        A 2D numpy array (shape: GRID_HEIGHT x GRID_WIDTH) of integers:
          0 = empty
          1 = snake (any segment)
          2 = apple
          3 = trap
    Action:
        Discrete(4) – 0: UP, 1: DOWN, 2: LEFT, 3: RIGHT.
    Reward:
        • + (10 + len(snake) + number_of_traps) when eating an apple.
        • -10 when hitting a trap (and the snake’s length is cut to half).
        • -0.1 per normal move.
        • -100 if the snake collides with the wall or itself (episode termination).
    """
    metadata = {'render.modes': ['human', 'rgb_array']}

    def __init__(self):
        super(SnakeEnv, self).__init__()
        self.grid_width = GRID_WIDTH
        self.grid_height = GRID_HEIGHT

        # Define action and observation spaces.
        self.action_space = spaces.Discrete(4)  # 4 possible directions.
        # Observation: grid with values in {0,1,2,3}
        self.observation_space = spaces.Box(low=0, high=3,
                                            shape=(self.grid_height, self.grid_width),
                                            dtype=np.int8)

        # How many steps between adding a new trap.
        self.trap_interval = 10  
        self.steps_since_last_trap = 0

        # Pygame rendering attributes.
        self.window = None
        self.clock = None
        self._init_pygame()

        self.reset()

    def _init_pygame(self):
        """Initialize Pygame for rendering."""
        pygame.init()
        self.window = pygame.display.set_mode((self.grid_width * CELL_SIZE,
                                                self.grid_height * CELL_SIZE))
        pygame.display.set_caption("Snake RL Environment")
        self.clock = pygame.time.Clock()

    def _get_random_free_position(self, occupied):
        """Return a random (x,y) not in the occupied set."""
        while True:
            pos = (random.randint(0, self.grid_width - 1),
                   random.randint(0, self.grid_height - 1))
            if pos not in occupied:
                return pos

    def _get_observation(self):
        """Return the current grid state as a numpy array."""
        obs = np.zeros((self.grid_height, self.grid_width), dtype=np.int8)
        # Mark snake segments as 1.
        for (x, y) in self.snake:
            obs[y, x] = 1
        # Mark the apple as 2.
        ax, ay = self.apple
        obs[ay, ax] = 2
        # Mark traps as 3.
        for (x, y) in self.traps:
            obs[y, x] = 3
        return obs

    def reset(self):
        """Reset the environment state and return the initial observation."""
        # Initialize snake at center with 3 segments.
        mid_x, mid_y = self.grid_width // 2, self.grid_height // 2
        self.snake = [
            (mid_x, mid_y),
            (mid_x - 1, mid_y),
            (mid_x - 2, mid_y)
        ]
        # Start moving to the right.
        self.current_direction = ACTION_TO_DIRECTION[3]
        # Place the first apple.
        occupied = set(self.snake)
        self.apple = self._get_random_free_position(occupied)
        self.apple_color = random.choice(APPLE_COLORS)
        self.traps = []
        self.steps_since_last_trap = 0
        self.score = 0
        self.done = False
        return self._get_observation()

    def step(self, action):
        """
        Execute one time step within the environment.
        """
        # Prevent reversal if snake has length > 1.
        if len(self.snake) > 1:
            current_action = self._direction_to_action(self.current_direction)
            if action == OPPOSITE_ACTION[current_action]:
                action = current_action

        # Update current direction.
        # Ensure action is an integer if it's a numpy array. - EPA correction with CoPilot help for type casting 02/03/2025 7:22 pm
            if isinstance(action, np.ndarray):
                action = action.item()
        self.current_direction = ACTION_TO_DIRECTION[action]

        head_x, head_y = self.snake[0]
        dx, dy = self.current_direction
        new_head = (head_x + dx, head_y + dy)

        # Check wall collision.
        if not (0 <= new_head[0] < self.grid_width and 0 <= new_head[1] < self.grid_height):
            self.done = True
            reward = -100
            return self._get_observation(), reward, self.done, {}

        # Check collision with self.
        if new_head in self.snake:
            self.done = True
            reward = -100
            return self._get_observation(), reward, self.done, {}

        # Default reward per move.
        reward = -0.1

        # Apple eaten?
        if new_head == self.apple:
            self.snake.insert(0, new_head)  # Grow snake.
            apple_reward = 10 + len(self.snake) + len(self.traps)
            reward = apple_reward
            self.score += apple_reward
            # Place a new apple.
            occupied = set(self.snake) | set(self.traps)
            self.apple = self._get_random_free_position(occupied)
            self.apple_color = random.choice(APPLE_COLORS)
        # Hit a trap?
        elif new_head in self.traps:
            self.snake.insert(0, new_head)
            # Cut snake length to half (minimum length 1).
            new_length = max(1, len(self.snake) // 2)
            self.snake = self.snake[:new_length]
            reward = -10
        else:
            # Normal move: advance the snake.
            self.snake.insert(0, new_head)
            self.snake.pop()

        # Update trap counter and add a trap if interval reached.
        self.steps_since_last_trap += 1
        if self.steps_since_last_trap >= self.trap_interval:
            occupied = set(self.snake) | set(self.traps) | {self.apple}
            new_trap = self._get_random_free_position(occupied)
            self.traps.append(new_trap)
            self.steps_since_last_trap = 0

        return self._get_observation(), reward, self.done, {}

    def _direction_to_action(self, direction):
        """Convert a (dx, dy) tuple into an action number."""
        for action, d in ACTION_TO_DIRECTION.items():
            if d == direction:
                return action
        return 3  # Default to RIGHT.

    def render(self, mode='human'):
        """Render the current state using Pygame."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.close()

        self.window.fill(COLOR_BG)

        # Optionally draw grid lines.
        for x in range(self.grid_width):
            for y in range(self.grid_height):
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(self.window, COLOR_GRID, rect, 1)

        # Draw traps.
        for (x, y) in self.traps:
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(self.window, COLOR_TRAP, rect)

        # Draw the apple.
        ax, ay = self.apple
        rect = pygame.Rect(ax * CELL_SIZE, ay * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(self.window, self.apple_color, rect)

        # Draw the snake.
        for (x, y) in self.snake:
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(self.window, COLOR_SNAKE, rect)

        pygame.display.flip()
        self.clock.tick(10)  # Limit to 10 FPS.

    def close(self):
        pygame.quit()


# --- Training the RL Agent ---
#
# We use Stable Baselines3’s DQN to train an agent on our custom SnakeEnv.
#
# The training loop is handled by the library’s .learn() method.
#
if __name__ == "__main__":
    # Create the environment.
    env = SnakeEnv()

    # (Optional) Check that the environment follows the Gym API.
    # from stable_baselines3.common.env_checker import check_env
    # check_env(env, warn=True)

    # Import DQN from stable_baselines3.
    from stable_baselines3 import DQN

    # Create the DQN model using a multilayer perceptron (MLP) policy.
    model = DQN("MlpPolicy", env, verbose=1)

    # Train the model for a specified number of timesteps.
    total_timesteps = 100000  # Adjust as needed.
    model.learn(total_timesteps=total_timesteps)

    # Save the trained model.
    model.save("dqn_snake_model")

    print("Training complete. Now running an evaluation...")

    # --- Evaluation Loop ---
    obs = env.reset()
    done = False
    print("Starting evaluation. Close the window to exit.")
    while not done:
        # Predict an action using the trained model.
        action, _ = model.predict(obs, deterministic=True)
        obs, reward, done, info = env.step(action)
        env.render()
        # Wait for a short time (in milliseconds) to slow down the display.
        pygame.time.wait(100)

    # Once the episode is done, keep the window open until the user closes it.
    print("Evaluation complete. Press the window close button to exit.")
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    env.close()

    """
    ### old code
    obs = env.reset()
    done = False
    while not done:
        # Predict an action using the trained model.
        action, _ = model.predict(obs, deterministic=True)
        obs, reward, done, info = env.step(action)
        env.render()

    env.close()
     
    """

