# Autonomous-SnakeByte
This is a self-playing AI-assisted coded using o3 mini-High or later showing fairly robust coding competence
snake_game<ver>.py is the latest iteration which has all the self-corrections from o3 model.

In particular, the first prototype snake_game.py was very good but simplistic.
snake_game2.py introduced constraints i.e. random blockers appearing every second which the snake must evade and also introduced the notion of the snake evading itself 
snake_game2b.py is a minor modification to include a sound (.wav) for every apple eaten but at this time we noticed the BFS algorithm took priority on evasive tactics for not running into a brick and it ended up not eating any apples. It did not die due to collision but it lost from starvation.

![image](https://github.com/user-attachments/assets/34d9b2a8-354f-4994-8f56-674410c3366e)

snake_game3.py this appears to have fixed the AI optimization logic to at least a level of competence that tries to eat an apple whenever there is a safe path 
Observation: o3-mini-high appears reasonable enough to self-correct certain algorithms with some minimal prompting.

p.s. Some of the other supporting python code here like Make_Burp_Sound.py was also coded via o3-mini-high and it is used sparingly to create synthetic sounds (e.g. chirp.wav is same as burp.wav) for sound effect when an apple is eaten.
Further exercise for the reader is to make other sounds when the game ends and when a snake hits a brick or itself causing some kind of penalty (presently halving the length of the snake and we can use the length as a factor for scoring, e.g. a multiplier to bonus points when an apple of certain color or category is eaten).
We can also ask o3 to add every move of the snake a concise move sound like the original game
