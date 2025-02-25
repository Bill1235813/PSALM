You control a robot that can take the following actions to build complex structures.

move: Move from a position to another, format: (move [pos_from] [pos_to] [height])
The new position and the old position must be at the same height.

move-up: Move up from a position to another, format: (move-up [pos_from] [height_from] [pos_to] [height_to])
The height at the new position is one block higher than the old position.

move-down: Move down from a position to another, format: (move-down [pos_from] [height_from] [pos_to] [height_to])
The height at the new position is one block lower than the old position.

place-block: Place a block at a neighboring position from the robot's current position, format: (place-block [pos_at] [pos_place] [height_at] [height_place])
The robot must have a block. The current height at the robot's position and the block's position must be the same. A block cannot be placed at the depot. The height at the block's position will be one block higher than the current height.

remove-block: Remove a block at a neighboring position from the robot's current position, format: (remove-block [pos_at] [pos_remove] [height_at] [height_remove])
The robot must not have a block. A block cannot be removed from the depot. The current height at the robot's position must be the same as the new height at the block's position. The new height at the block's position will be one block lower than the current height.

create-block: Create a block at the depot, format: (create-block [pos])
The robot will have the block.

destroy-block: Destroy a block at the depot, format: (destroy-block [pos])
The robot must have a block.