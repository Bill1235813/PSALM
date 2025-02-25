#!/bin/bash
#source ~/.bashrc
#conda activate base

#domain=$1 # blockworld, barman, gripper, floortile, termes, tyreworld
#method=$2 # llm_planner, llm_ic_planner, llm_pddl_planner, llm_ic_pddl_planner
#task=$3
#run=$4
#timelimit=200
#
#python main.py --domain $domain --method $method --task $task --run $run --time-limit $timelimit > trainlogs/$domain\_$method\_$task\_$timelimit\_$run.log

for DOMAIN in storage
do
python run_env.py --number_prospection 10 --domain $DOMAIN --max_run 1000 --task 2 --sample_traj_method rand_check_state
done


for DOMAIN in floortile barman termes tyreworld
do
python run_env.py --number_prospection 10 --domain $DOMAIN --max_run 1000 --task 0 --sample_traj_method rand_check_state
done

for DOMAIN in grippers blocksworld
do
python run_env.py --number_prospection 10 --domain $DOMAIN --max_run 1000 --task 1 --sample_traj_method rand_check_state
done

#seq-opt-fdss-1, lama-first, seq-sat-lama-2011, seq-sat-fd-autotune-1, seq-opt-lmcut
