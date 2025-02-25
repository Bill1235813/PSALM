(define (domain gripper-strips)
 (:requirements :strips :typing)
 (:types room object robot gripper)
 (:predicates (at-robby ?r - robot ?x - room)
 	      (at ?o - object ?x - room)
	      (free ?r - robot ?g - gripper)
	      (carry ?r - robot ?o - object ?g - gripper))

   (:action move
       :parameters  (?r - robot ?from ?to - room)
       :precondition (and  [[move_pre]])
       :effect (and  [[move_post]]))

   (:action pick
       :parameters (?r - robot ?obj - object ?room - room ?g - gripper)
       :precondition (and  [[pick_pre]])
       :effect (and  [[pick_post]]))

   (:action drop
       :parameters (?r - robot ?obj - object ?room - room ?g - gripper)
       :precondition (and  [[drop_pre]])
       :effect (and  [[drop_post]])))