import pygame

from stable_baselines3 import DQN
from snake_gameRL1 import SnakeEnv  # Ensure your SnakeEnv is accessible

# Load the trained model.
model = DQN.load("dqn_snake_model")

# Create the environment.
env = SnakeEnv()

# Optionally, run the agent.
obs = env.reset()
done = False
while not done:
    action, _ = model.predict(obs, deterministic=True)
    obs, reward, done, info = env.step(action)
    env.render()
    # Slow down if needed; in case the game ends too fast
    pygame.time.wait(100)

env.close()
