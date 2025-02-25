The domain assumes a world where there are a set of blocks that can be stacked on top of each other, an arm that can hold one block at a time, and a table where blocks can be placed. The robot has 4 actions:

pickup: allows the arm to pick up a block from the table if it is clear and the arm is empty, format: (pickup [object])
After the pickup action, the arm will be holding the block, and the block will no longer be on the table or clear.

putdown: allows the arm to put down a block on the table if it is holding a block, format: (putdown [object])
After the putdown action, the arm will be empty, and the block will be on the table and clear.

stack: allows the arm to stack a block on top of another block if the arm is holding the top block and the bottom block is clear, format: (stack [object] [object-under])
After the stack action, the arm will be empty, the top block will be on top of the bottom block, and the bottom block will no longer be clear.

unstack: allows the arm to unstack a block from on top of another block if the arm is empty and the top block is clear, format: (unstack [object] [object-under])
After the unstack action, the arm will be holding the top block, the top block will no longer be on top of the bottom block, and the bottom block will be clear.