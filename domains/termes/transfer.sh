#!/bin/bash

declare -a rows=("4")
declare -a cols=("3")
declare -a robot_locs=("2 0")

arraylength=${#rows[@]}

for (( i=0; i<${arraylength}; i++ ));
do
  python transfer.py --row ${rows[$i]} --col ${cols[$i]}  --robot_loc ${robot_locs[$i]} --problem_id $(($i))
done
