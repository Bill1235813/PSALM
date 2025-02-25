#!/bin/bash

declare -a rows=("2" "5" "5" "5" "5" "5" "5" "6" "6" "6" "6" "6" "6" "6" "6" "6")
declare -a cols=("3" "3" "3" "3" "4" "4" "4" "3" "3" "3" "4" "4" "4" "5" "5" "5")
declare -a black_locs=("1 2" "4 1" "4 1" "1 1" "3 4" "2 4" "0 3" "4 1" "5 3" "4 2" "1 1" "5 2" "2 3" "3 3" "5 4" "5 5")
declare -a white_locs=("0 1" "4 3" "3 2" "2 3" "0 3" "4 1" "1 1" "3 3" "4 2" "0 3" "1 3" "1 3" "1 4" "0 5" "2 2" "3 4")
declare -a upper_right_colors=("white" "black" "black" "black" "white" "white" "white" "white" "white" "white" "black" "black" "black" "white" "white" "white")

arraylength=${#rows[@]}

for (( i=0; i<${arraylength}; i++ ));
do
  python transfer.py --row ${rows[$i]} --col ${cols[$i]}  --black_loc ${black_locs[$i]} --white_loc ${white_locs[$i]} \
    --upper_right_color ${upper_right_colors[$i]} --problem_id $(($i))
done
