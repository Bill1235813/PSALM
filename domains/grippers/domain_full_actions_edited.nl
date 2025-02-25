You have a set of robots, each with a gripper that can move objects between different rooms. There are 3 actions defined in this domain:

move: this action allows a robot to move from one room to another, format: (move [robot] [room_from] [room_to])
The action has a single precondition, which is that the robot is currently in a room.
The effect of this action is to move the robot to another room and to remove the fact that it is in the original room.

pick: this action allows a robot to pick up an object using the gripper, format: (pick [robot] [object] [room] [gripper])
The action has three preconditions: (1) the object is located in a room (2) the robot is currently in the same room and (3) the gripper is free (i.e., not holding any object).
The effect of this action is to update the state of the world to show that the robot is carrying the object using the gripper, the object is no longer in the room, and the gripper is no longer free.

drop: this action allows a robot to drop an object that it is carrying, format: (drop [robot] [object] [room] [gripper])
The action has two preconditions: (1) the robot is currently carrying the object using the gripper, and (2) the robot is currently in a room.
The effect of this action is to update the state of the world to show that the robot is no longer carrying the object using the gripper, the object is now located in the room, and the gripper is now free.