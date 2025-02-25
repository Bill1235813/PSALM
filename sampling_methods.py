import os
import copy
import re
import numpy as np

from utils import state_transition, construct_param_to_obj, parse_pddl_attr_from_string


def clean_llm_plan(args, domain, exp_base_folder):
    def clean_llm_action(s):
        a_strs, _ = parse_pddl_attr_from_string(s, attr_starter="(")
        if not isinstance(a_strs, list):
            a_strs = [a_strs]
        verified_action_str = ""

        for a_str in a_strs:
            parsed_a_str = re.compile("([\w-]+)").findall(a_str)
            if len(parsed_a_str) > 0:
                a_name = parsed_a_str[0]
                a_params = parsed_a_str[1:]
                try:
                    a_index = domain.action_name.index(a_name)
                    for a_type, a_param in zip(domain.action_params_dict[a_index].values(), a_params):
                        if a_param not in domain.task_type_object_matching[args.task][a_type]:
                            continue
                except:
                    continue
                # pass the check
                verified_action_str += f"({a_name} {' '.join(a_params)})\n"
        return verified_action_str

    for i in range(args.number_rollout):
        text_plan_file_name = f"{exp_base_folder}/p{args.task}_plan{i}"
        text_plan_lines = open(text_plan_file_name).read().splitlines()
        verified_text_plan_str = ""
        for l in text_plan_lines:
            verified_text_plan_str += clean_llm_action(l)
        with open(text_plan_file_name, "w") as f:
            f.write(verified_text_plan_str)

    return text_plan_file_name


def llm_ic_sampler(args, agent, domain, memory, cand_traj, exp_base_folder):
    """
    Baseline method:
        The LLM will be asked to directly give a plan based on the task description.
    """
    context_nl, _, context_sol = domain.examples

    task = args.task
    if os.path.exists(f"{exp_base_folder}/p{task}_plan{args.number_rollout - 1}") and not args.rerun:
        return

    # A. generate prompt and record it
    context_init_pddl = "(" + '\n'.join(domain.example_init) + ")"
    task_init_pddl = "(" + '\n'.join(domain.task_init_state[args.task]) + ")"
    if memory is not None and len(memory.previous_trajs) > 0:
        filtered_trajs = list(filter(lambda x: len(x[0]) >= 3, memory.previous_trajs))
        failed_index = np.random.choice(len(filtered_trajs), min(args.max_failed_traj, len(filtered_trajs)),
                                        replace=False)
        failed_traj = [filtered_trajs[i] for i in failed_index]
        failed_traj_str = agent.failed_traj_str_starter
        for i, (traj, err_msg) in enumerate(failed_traj):
            failed_traj_str += f"Failed traj {i}:\n"
            failed_traj_str += "\n".join(traj) + "\n" + err_msg + "\n"
        failed_traj_str += "\n"
        current_action_desp = memory.current_action_desp
    else:
        failed_traj_str = ""
        current_action_desp = ""
    prompt = agent.lm_ic_prompt.replace("[[domain_nl]]", domain.domain_nl) \
        .replace("[[action_description]]", current_action_desp) \
        .replace("[[domain_type_pred]]", domain.domain_type_pred_str) \
        .replace("[[context_nl]]", context_nl) \
        .replace("[[context_init]]", context_init_pddl) \
        .replace("[[context_pddl]]", domain.tasks_pddl[args.task]) \
        .replace("[[context_sol]]", context_sol) \
        .replace("[[task_nl]]", domain.tasks_nl[args.task]) \
        .replace("[[task_init]]", task_init_pddl) \
        .replace("[[task_pddl]]", domain.tasks_pddl[args.task]) \
        .replace("[[cand_action_list]]", cand_traj) \
        .replace("[[failed_traj]]", failed_traj_str) \
        .replace("[[domain_acthead_pddl]]", domain.domain_acthead_pddl)

    if args.save_verbose:
        with open(f"{exp_base_folder}/p{task}_prompt_rollout", "w") as f:
            f.write(prompt)

    # B. prompt the plan and record it
    for i in range(args.number_rollout):
        text_plan = agent.query(prompt, temperature=0.8)
        text_plan_file_name = f"{exp_base_folder}/p{task}_plan{i}"
        with open(text_plan_file_name, "w") as f:
            f.write(text_plan)

    return clean_llm_plan(args, domain, exp_base_folder)


def rand_sampler(args, agent, domain, memory, cand_traj, exp_base_folder, check_state=False):
    task = args.task
    if os.path.exists(f"{exp_base_folder}/p{task}_plan{args.number_rollout - 1}") and not args.rerun:
        return

    prev_state = None
    if len(cand_traj.split("\n")) > 1:
        cand_traj = [traj for traj in cand_traj.split("\n") if traj.startswith("(")]
        if check_state:
            prev_state = copy.copy(domain.task_init_state[args.task])
            for cand_a in cand_traj:
                param_to_obj, a_name = construct_param_to_obj(domain, cand_a)
                prev_state = state_transition(prev_state, memory.sampled_dicts[-1][f"{a_name}_post"], param_to_obj)
        cand_traj = "\n".join(cand_traj)

    for i in range(args.number_rollout):
        if check_state:
            if prev_state is not None:
                state = copy.copy(prev_state)
            else:
                state = copy.copy(domain.task_init_state[args.task])

            rand_actions = []
            for _ in range(args.number_prospection):
                if state is not None:
                    rand_action, state = domain.get_task_one_explored_action(task, state, memory)
                else:  # dead end
                    rand_action = domain.get_task_one_random_action(task)
                rand_actions.append(rand_action)
        else:
            rand_actions = [domain.get_task_one_random_action(task) for _ in range(args.number_prospection)]
        print(rand_actions)
        rand_actions = "\n".join(rand_actions)
        text_plan = f"{cand_traj}\n{rand_actions}"
        text_plan_file_name = f"{exp_base_folder}/p{task}_plan{i}"
        with open(text_plan_file_name, "w") as f:
            f.write(text_plan)


def rand_check_state_sampler(args, agent, domain, memory, cand_traj, exp_base_folder):
    return rand_sampler(args, agent, domain, memory, cand_traj, exp_base_folder, check_state=True)
