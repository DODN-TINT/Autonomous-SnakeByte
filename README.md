# Autonomous-SnakeByte
This is a self-playing AI-assisted coded using o3 mini-High or later showing fairly robust coding competence using pygame (and some stuff for timer and sounds) as a library

snake_game<ver>.py is the latest iteration which has all the self-corrections from o3 model.

In particular, the first prototype snake_game.py was very good but simplistic.
snake_game2.py introduced constraints i.e. random blockers appearing every second which the snake must evade and also introduced the notion of the snake evading itself 
snake_game2b.py is a minor modification to include a sound (.wav) for every apple eaten but at this time we noticed the BFS algorithm took priority on evasive tactics for not running into a brick and it ended up not eating any apples. It did not die due to collision but it lost from starvation.

**Snake Game Screen Shot of a 20x20 grid**
snake is green, apples are red (single category for now), and bricks are purple

![image](https://github.com/user-attachments/assets/34d9b2a8-354f-4994-8f56-674410c3366e)

snake_game3.py this appears to have fixed the AI optimization logic to at least a level of competence that tries to eat an apple whenever there is a safe path 
Observation: o3-mini-high appears reasonable enough to self-correct certain algorithms with some minimal prompting.

snake_game3B.py adds scoring proportionate to length of snake and apples eaten, and penalty for crashing into traps or itself. Plus some simple arcade sounds to indicate apple eaten or some crash. The AI snake moving and navigating logic is still BFS.
![Snake Game OK Score 876 with BFS](https://github.com/user-attachments/assets/af979281-abbe-48d5-b7b2-580f02186db8)

snake_gameRL1.py is the output code asking o3-mini-high to improve and train itself better using ML. It came up with the suggestion for RL and using DQN as an approach and pulled in openAI gym etc. I used this to train the DQN model then evaluate it as well. 
![SnakeEnv learning with openAI Gym for RL (shimmy)](https://github.com/user-attachments/assets/ab30cd1d-9c74-4631-8c68-53bf5a25fd8e)
![Snake Game Training 02 -3280 Episodes Done](https://github.com/user-attachments/assets/49b80e81-5b44-4c75-8779-65d0496966e2)

snake_game-useDQNModel.py is a stand alone utility python script to just load an existing model and play with it.

Finally, we have snake 3B-DQN.py that factors out BFS AI logic and pulls in instead the model from DQN training into the 3B variant with sounds and scoring.
The high score for this approach is nearly 3674 points and the screenshot here ![image](https://github.com/user-attachments/assets/8937d7ca-980c-43e2-a17a-8beb64ce79f6) is more than 3200 while it is still playing by itself.

Some of the other supporting python code here like Make_Burp_Sound.py was also coded via o3-mini-high and it is used sparingly to create synthetic sounds (e.g. chirp.wav is same as burp.wav) for sound effect when an apple is eaten.
Further exercise for the reader is to make other sounds when the game ends and when a snake hits a brick or itself causing some kind of penalty (presently halving the length of the snake and we can use the length as a factor for scoring, e.g. a multiplier to bonus points when an apple of certain color or category is eaten).
We can also ask o3 to add every move of the snake a concise move sound like the original game
