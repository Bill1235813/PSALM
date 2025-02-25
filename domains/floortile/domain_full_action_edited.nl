You control a set of robots that use different colors to paint patterns in floor tiles. The robots can move around the floor tiles in four directions (up, down, left and right). Robots paint with one color at a time, but can change their spray guns to any available color. However, robots can only paint the tile that is in front (up) and behind (down) them, and once a tile has been painted no robot can stand on it.

Here are 7 actions each robot can do:
change-color: Change the spray gun color, format: (change-color [robot] [color-before] [color-after])
paint-up: Paint the tile that is up from the robot, format: (paint-up [robot] [tile-to-paint] [tile-at] [color])
paint-down: Paint the tile that is down from the robot, format: (paint-down [robot] [tile-to-paint] [tile-at] [color])
up: Move up, format: (up [robot] [tile-at] [tile-to])
down: Move down, format: (down [robot] [tile-at] [tile-to])
right: Move right, format: (right [robot] [tile-at] [tile-to])
left: Move left, format: (left [robot] [tile-at] [tile-to])

You have the following restrictions on your actions:
A robot can only paint a tile if the tile has not been painted.
A robot can only paint a tile to the color of its spray gun.
A robot cannot move to a tile that has been painted.
