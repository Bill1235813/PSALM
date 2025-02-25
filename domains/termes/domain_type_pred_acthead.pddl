(define (domain termes)
(:requirements :typing :negative-preconditions)
(:types
    numb - object
    position - object
)
(:predicates
    (height ?p - position ?h - numb)
    (at ?p - position)
    (has-block)
    ;
    ; static predicates
    (SUCC ?n1 - numb ?n2 - numb)
    (NEIGHBOR ?p1 - position ?p2 - position)
    (IS-DEPOT ?p - position)
)
(:action move
    :parameters (?from - position ?to - position ?h - numb)
    :precondition (and [[move_pre]])
    :effect (and [[move_post]])
)

(:action move-up
    :parameters (?from - position ?hfrom - numb ?to - position ?hto - numb)
    :precondition (and [[move-up_pre]])
    :effect (and [[move-up_post]])
)

(:action move-down
    :parameters (?from - position ?hfrom - numb ?to - position ?hto - numb)
    :precondition (and [[move-down_pre]])
    :effect (and [[move-down_post]])
)

(:action place-block
    :parameters (?rpos - position ?bpos - position ?hbefore - numb ?hafter - numb)
    :precondition (and [[place-block_pre]])
    :effect (and [[place-block_post]])
)

(:action remove-block
    :parameters (?rpos - position ?bpos - position ?hbefore - numb ?hafter - numb)
    :precondition (and [[remove-block_pre]])
    :effect (and [[remove-block_post]])
)

(:action create-block
    :parameters (?p - position)
    :precondition (and [[create-block_pre]])
    :effect (and [[create-block_post]])
)

(:action destroy-block
    :parameters (?p - position)
    :precondition (and [[destroy-block_pre]])
    :effect (and [[destroy-block_post]])
)

)