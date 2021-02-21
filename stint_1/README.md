# Brick Breaker CLI-based Game
### - By Anmol Agarwal
## Introduction
This is a command line version of the famous Brick Breaker game (first released by BlackBerry) written in Python-3 .

In the game,the player must smash a wall of bricks by deflecting a bouncing ball with a paddle. The paddle may move horizontally and is controlled with the 'A' and 'D' keys.
The player gets some fixed number of lives to start with (can be changed in the `config.py` file); a life is lost if the ball hits the bottom of the screen. There are different types of bricks with varying strengths and properties in the brick structure. Also, it is possible to take help of different powerups along the game. The player must try to break all the breakable bricks within a fixed time limit.

#### Gameplay
The functionality has been inspired from [here](https://www.youtube.com/watch?v=BXEk0IHzHOM)

## Controls
- <kbd>a</kbd>: Move paddle towards the left
- <kbd>d</kbd>: Move paddle towards the right
- <kbd>s</kbd>: Release the ball from the paddle

---
## Scoring System (can be modified in the  `config.py`)
* Breakable brick destroyed= 1 or 2 or 3 depending on the strength of the brick
* Unbreakable brick destroyed= 4 pts
* Explosive brick destroyed= 5 pts
* activation of a powerup=20 pts
* Number of lives left (allotted only if level has been cleared)= 20 pts


## Rules and Design Choices
- When a ThruBall powerup is activated, there were two possible options: either give this ability to all balls or only to those balls present at the time of powerup being activated. I could not find an occurrence of such a test case in the original brick breaker game and hence, went forward with the 2nd option.
- Time is not getting resetted every time a life is lost.
- I consider the game to be won as soon as all the breakable bricks (normal bricks + explosive bricks) are broken. I am not considering the unbreakable bricks for determining win/lose status.
- PaddleGrab is activated for a greater time than other powerups.
- Since there is the possibility that the ball gets stuck in an infinite collision configuration (the deactivation of the FastBall powerup is like a non-conservative force), I have implemented a total time limit within which the game needs to be finished
- An attempt is considered successful if all the bricks (except the unbreakable ones) are destroyed
- The Ball velocity depends on where it hits the paddle
- On hitting an explosive brick, a chain reaction is set up which tries 
- Currently, the effect of FastBall powerup is limited to ball's horizontal velocity only. This can be modified to affect vertical velocity as well by changing the flag variable at an indicated place in the code.
- logging library was allowed after discussion with TA (does not affect game functionality in any way)



## Base Classes implemented
 * `Game`: handles entity creation,entity movement tracking,  collisions, velocity manipulations, game lives
 * `Canvas`: handles rendering of the entities on the terminal window
 * `InputHelper`: handles keyboard input, restoring settings
 * `PaddleClass`: handles paddle movement, magnetizing of paddle, paddle length manipulation etc
 * `BricksClass`: has several derived classes which together handle recursive brick breaking, tracking of brick strength
 * `PowerupsClass`: has several derived classes which together handle movement of powerups, activation and deactivations specific to the resepctive powerups, time remaining before deactivation etc 
`BallClass`: handles ball movement, velocity modification, stickiness to paddle etc.


## Object Oriented Concepts
### Inheritance
* The `UnbreakableBrick`, `NormalBrick`,`ExplosiveBrick` classes all inherit the `BricksClass` class.
* The `ExpandPaddle`, `ShrinkPaddle`, `FastBall`, `ThruBall`, `PaddleGrab`, `BallMultiplier`  classes all inherit the `PowerupsClass` class.

### Polymorphism
* The `get_unlucky_neighbours()` method defined in the `PowerupsClass` class has been overriden in the `ExpandPaddle`, `ShrinkPaddle`, `FastBall`, `ThruBall`, `PaddleGrab` classes. [method over-riding]
* The `deactivate_powerup()` method defined in the `BricksClass` class has been overriden in the `ExplosiveBrick` class. [method over-riding]
* The `hit_brick()` method defined in `Game` class has been overloaded (atleast by the defn of overloading for Python OOP [here](https://stackoverflow.com/a/6434546/6427607))

### Encapsulation
All the game entities and functions have been implemented using different base classes, objects, derived classes, static methods, getters and setters. The class-object paradigm helps encapsulate logically different components of the game.

### Abstraction
Intuitive functions like the ones below hide away the inner details from the user and improves readability of code.
* `BallClass.release()`
* `BallClass.capture()`
* `BallClass.move_horizontally()`
* `BallClass.move_vertically()`
* `PaddleClass.magnetize()`
* `PaddleClass.demagnetize()`
* `BricksClass.damage()`
* `PowerupsClass.move()`
* `PowerupsClass.activate_powerup()`
* `PowerupsClass.deactivate_powerup()`
* `PowerupsClass.eliminate()`

## Playing the game
After downloading all the files, run the following in the terminal.
   ```(shell)
   $ python3 play.py
   ```
   
 The game events can be monitored by running 
  ```(shell)
   $ tail -f test.log
   ```