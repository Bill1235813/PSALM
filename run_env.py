import argparse
import os
import time
import subprocess
import re
import shutil
import utils
from domains import ALL_DOMAINS, Domain
from agent import Agent
from memory import Memory
from evaluator import Evaluator, METRICS

from sampling_methods import llm_ic_sampler, rand_sampler, rand_check_state_sampler
from cnf_prediction_methods import llm_infer_cnf, rule_based_cnf
from plot import plot_metrics

FAST_DOWNWARD_ALIAS = "lama-first"
# FAST_DOWNWARD_ALIAS = "seq-opt-fdss-1"


def get_cand_trajs(args, agent, domain, memory, exp_base_folder):
    if os.path.exists(f"{exp_base_folder}/p{args.task}_cand_trajs") and not args.rerun:
        cand_trajs_str = open(f"{exp_base_folder}/p{args.task}_cand_trajs").read()
        have_plan = False
    else:
        plan_file_name = os.path.join(exp_base_folder, f"p{args.task}_pddl_plan")
        if len(memory.sampled_dicts) <= 1:
            cand_trajs_str, have_plan = "", False
        elif os.path.exists(plan_file_name) and not args.rerun:
            cand_trajs_str, have_plan = "", True
        else:
            task_nl_file, task_pddl_file = domain.get_task_file(args.task)
            new_domain_file = os.path.join(exp_base_folder, "new_domain.pddl")
            if args.save_verbose:
                log_file = f"{exp_base_folder}/solver_log"
            else:
                log_file = "/dev/null"
            os.system(f"python ./downward/fast-downward.py --alias {FAST_DOWNWARD_ALIAS} " + \
                      f"--search-time-limit {args.time_limit} --plan-file {plan_file_name} " + \
                      f"{new_domain_file} {task_pddl_file} > {log_file}")

            have_plan = os.path.exists(plan_file_name)
            cand_trajs_str = ""

        if have_plan:  # check if plan is a prefix of a wrong plan
            solver_plan = [action for action in open(plan_file_name).read().split("\n") if action.startswith("(")]
            have_plan = not utils.check_any_prefix_plans(solver_plan, memory.previous_trajs)
        elif os.path.exists(args.cand_traj_file):  # no plan but have cand trajs
            cand_trajs = open(args.cand_traj_file).read()
            cand_trajs = set(re.split(r"Step \d+:\n", cand_trajs)[1:])
            if cand_trajs:
                cand_trajs_str = agent.cand_traj_str_starter if args.sample_traj_method == "llm_ic" else ""
                top_cand_trajs = sorted(cand_trajs, key=lambda x: len(x), reverse=True)[:args.number_cand_traj]
                for i, trajs in enumerate(top_cand_trajs):
                    edited_trajs = "\n".join(["(" + c + ")" for c in trajs.strip().split("\n")])
                    cand_trajs_str += f"Option {i}:\n{edited_trajs}\n"
                cand_trajs_str += "\n"
                if args.save_verbose:
                    with open(f"{exp_base_folder}/p{args.task}_cand_trajs", "w") as f:
                        f.write(cand_trajs_str)

    return cand_trajs_str, have_plan


def validate_plans(args, domain, exp_base_folder, from_solver=False):
    def log_plan_status(output):
        if "Plan valid" in output:
            print("Plan valid.")
            return True
        elif "Goal not satisfied" in output:
            print("Executable plan but goal not satisfied.")
            return False
        else:
            print("Non-executable plan.")
            return False

    domain_pddl_file = domain.get_domain_valid_pddl_file()
    task_nl_file, task_pddl_file = domain.get_task_file(args.task)

    valid_tag = False
    valid_outputs = []
    if from_solver:
        print(f"validate plan from solver, task {args.task}")
        plan = f"{exp_base_folder}/p{args.task}_pddl_plan"
        if not os.path.exists(f"{plan}_valid") or args.rerun:
            os.system(f"validate -v {domain_pddl_file} {task_pddl_file} {plan} > {plan}_valid")
        valid_output = open(f"{plan}_valid").read()
        valid_outputs.append(valid_output)
        valid_tag = log_plan_status(valid_output)
    else:
        for i in range(args.number_rollout):
            print(f"validate plan{i}, task {args.task}")
            plan = f"{exp_base_folder}/p{args.task}_plan{i}"
            if not os.path.exists(f"{plan}_valid") or args.rerun:
                os.system(f"validate -v {domain_pddl_file} {task_pddl_file} {plan} > {plan}_valid")
            valid_output = open(f"{plan}_valid").read()
            valid_outputs.append(valid_output)
            valid_tag = log_plan_status(valid_output)
    return valid_outputs, valid_tag


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LLM-Agent")
    parser.add_argument("--domain", type=str, choices=ALL_DOMAINS, default="grippers")
    parser.add_argument("--exp_name", type=str, default="debug9")
    parser.add_argument("--time-limit", type=int, default=100)
    parser.add_argument("--task", type=int, default=1)
    parser.add_argument("--number_rollout", type=int, default=1)
    parser.add_argument("--max_run", type=int, default=100)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--gamma", type=float, default=1)
    parser.add_argument("--alpha", type=float, default=1)
    parser.add_argument("--number_prospection", type=int, default=5)
    parser.add_argument("--cand_traj_file", type=str, default="progress_log")
    parser.add_argument("--number_cand_traj", type=int, default=1)
    parser.add_argument("--max_failed_traj", type=int, default=3)
    parser.add_argument("--sample_traj_method", type=str, choices=["llm_ic", "rand", "rand_check_state"],
                        default="llm_ic")
    parser.add_argument("--infer_cnf_method", type=str, choices=["llm_infer", "rule_based"], default="rule_based")
    parser.add_argument("--debug", action="store_true", default=True)
    parser.add_argument("--rerun", action="store_true", default=True)
    parser.add_argument("--save_verbose", action="store_true", default=True)
    args = parser.parse_args()

    utils.set_seed(args.seed)
    if os.path.exists(args.cand_traj_file):
        os.remove(args.cand_traj_file)

    # initialization of problem domain, agent and memory
    agent = Agent(args.rerun)
    domain = Domain(args.domain)
    memory = Memory(args, domain)
    evaluator = Evaluator(args, domain)
    exp_dir = f"./experiments/{args.exp_name}/{args.sample_traj_method}_{args.infer_cnf_method}/{domain.name}"

    # set timer
    start_time = time.time()
    sampling_method = eval(f"{args.sample_traj_method}_sampler")
    infer_method = eval(f"{args.infer_cnf_method}_cnf")

    for run in range(args.max_run):

        print(f"Run {run}:")

        # create the tmp / result folders
        exp_base_folder = f"{exp_dir}/run{run}"
        if not os.path.exists(exp_base_folder):
            os.system(f"mkdir -p {exp_base_folder}")

        # sample new domain file and create the corresponding action description (memory.current_action_desp)
        memory.sample_new_domain_file(args, agent, domain, exp_base_folder)

        # get candidate trajs from the solver, or a full plan (if any)
        solver_cand_trajs, have_plan = get_cand_trajs(args, agent, domain, memory, exp_base_folder)

        # sample new trajs using LLM / random / etc
        valid_tag = False
        llm_valid_tag = False
        if not have_plan:
            sampling_method(args, agent, domain, memory, solver_cand_trajs, exp_base_folder)
            valid_outputs, llm_valid_tag = validate_plans(args, domain, exp_base_folder, from_solver=False)
        else:
            valid_outputs, valid_tag = validate_plans(args, domain, exp_base_folder, from_solver=True)

        # CNF prediction from LLM / rule-based / LLM + rule / etc.
        cnf_dict, plans, post_actions, pre_actions, err_msgs = infer_method(args, agent, domain, memory, valid_outputs,
                                                                            exp_base_folder)
        evaluator.overall_steps += sum([len(plan) for plan in plans])
        print("Executed Step:", sum([len(plan) for plan in plans]))

        # update the memory
        if not valid_tag:
            memory.update(args, domain, cnf_dict, post_actions, pre_actions, exp_base_folder)
        if not llm_valid_tag:
            # print(plans, err_msgs)
            memory.previous_trajs += list(zip(plans, err_msgs))

        if valid_tag:
            break

        # evaluation
        evaluator.eval_score(memory.condition_dict, exp_base_folder)

    end_time = time.time()
    print(f"[info] task {args.task} takes {end_time - start_time} sec")
    print("Total resets:", run)
    print("Total steps: ", evaluator.overall_steps)

    # clean the tmp files if needed
    if not args.debug:
        shutil.rmtree(exp_dir)
        os.system(f"mkdir -p {exp_dir}")

    # save
    memory.save_predicted_domain_file(args, domain, exp_dir)
    memory.save_current_memory(exp_dir)
    evaluator.eval_score(memory.condition_dict, exp_dir)
    evaluator.save_metrics(exp_dir)

    # make visualization
    plot_metrics(exp_dir, args.domain, METRICS[:4])
