You are a robot barman that manipulates drink dispensers, shot glasses and a shaker. You have two hands. The goal is to find a plan that serves a desired set of drinks. Here are the 12 actions you can do:

grasp: Grasp a container, format: (grasp [hand] [container])
You can only grasp a container if your hand is empty and it is on the table.
Once you grasp a container, you are holding the container and the container is not on the table.

leave: Leave a container on the table, format: (leave [hand] [container])
You can only leave a container if you are holding it.
Once you leave a container on the table, your hand becomes empty.

fill-shot: Fill a shot glass with an ingredient, format: (fill-shot [shot] [ingredient] [hand-hold] [hand-empty] [dispenser])
You can only fill a shot glass if you are holding the shot glass, your other hand is empty, the shot glass is empty and clean.
Once you fill a shot glass, the shot glass contains the ingredient.

refill-shot: Refill a shot glass with an ingredient, format: (refill-shot [shot] [ingredient] [hand-hold] [hand-empty] [dispenser])
You can only refill a shot glass if you are holding the shot glass, your other hand is empty, the shot glass is empty and has contained the same ingredient before.
Once you refill a shot glass, the shot glass contains the ingredient.

empty-shot: Empty a shot glass, format: (empty-shot [hand] [shot] [beverage])
You can only empty a shot glass if you are holding the shot glass and it contains a beverage.
Once you empty a shot, the shot is empty but not clean.

clean-shot: Clean a shot glass, format: (clean-shot [shot] [beverage] [hand-hold] [hand-empty])
You can only clean a shot glass if you are holding the shot glass and it is empty, and your other hand is empty.
Once you clean a shot, the shot is clean.

pour-shot-to-clean-shaker: Pour an ingredient from a shot glass to a clean shaker, format: (pour-shot-to-clean-shaker [shot] [ingredient] [shaker] [hand] [level-before] [level-after])
You can only pour from a shot glass to a clean shaker if you are holding the shot glass, the shot glass contains an ingredient, and the shaker is empty and clean.
Once you pour an ingredient from a shot glass to a clean shaker, the shaker contains the ingredient and is at one level above the previous level, and the shot glass becomes empty but not clean.

pour-shot-to-used-shaker: Pour an ingredient from a shot glass to a used shaker, format: (pour-shot-to-used-shaker [shot] [ingredient] [shaker] [hand] [level-before] [level-after])
You can only pour from a shot glass to a used shaker if you are holding the shot glass, the shot glass contains an ingredient, the shaker is unshaked and at a level not full.
Once you pour an ingredient from a shot glass to a used shaker, the shaker contains the ingredient and is at one level above the previous level, and the shot glass becomes empty but not clean.

empty-shaker: Empty a shaker, format: (empty-shaker [hand] [shaker] [cocktail] [level-before] [level-empty])
You can only empty a shaker if you are holding the shaker and the shaker contains a shaked cocktail.
Once you empty a shaker, the shaker is at the empty level but not clean.

clean-shaker: Clean a shaker, format: (clean-shaker [hand-hold] [hand-empty] [shaker])
You can only clean a shaker if you are holding the shaker, your other hand is empty, and the shaker is empty.
Once you clean a shaker, the shaker is clean.

shake: Shake a cocktail in a shaker, format: (shake [cocktail] [ingredient-first] [ingredient-second] [shaker] [hand-hold] [hand-empty])
You can only shake a cocktail if you are holding the shaker, your other hand is empty, the shaker is unshaked, and the shaker contains two ingredients, and both ingredients are parts of a cocktail.
Once you shake, the two ingredients in the shaker become a cocktail.

pour-shaker-to-shot: Pour from a shaker to a shot glass, format: (pour-shaker-to-shot [beverage] [shot] [hand] [shaker] [level-before] [level-after])
You can only pour from a shaker to a shot glass if you are holding the shaker, the shaker contains the cocktail, the shaker is shaked, and the shot glass is empty and clean.
Once you pour from a shaker to a shot glass, the shot glass contains the beverage in the shaker, the shot glass is no longer clean and empty, and the shaker is at one level below the previous level.

Given a planning problem described as in the image, please provide a executable plan, in the way of a sequence of actions, to solve the problem. Follow the provided action format.