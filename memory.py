import itertools
import numpy as np
import os
import pickle
import json
import copy
from collections import defaultdict, Counter
from utils import split_cnf_prediction_by_parentheses, get_params_set, check_params_type


###############################################################################
#
# A memory that stores the predictions from LLM (trajectories; pre- and post-conditions)
#
###############################################################################


def convert_precondition_to_text(preconds):
    return "The preconditions are " + ", ".join(preconds) + "."


def convert_postcondition_to_text(postconds):
    return "The effects are " + ", ".join(postconds) + "."


def fill_in_action_desp(prompt, nl, name, params, precond, postcond):
    # prompt - [[action_nl]]: [[action_name]] [[action_params]]. [[action_precond]] [[action_postcond]]
    return prompt.replace("[[action_nl]]", nl) \
           .replace("[[action_name]]", name) \
           .replace("[[action_params]]", params) \
           .replace("[[action_precond]]", precond) \
           .replace("[[action_postcond]]", postcond).strip()


def sample_from_memory(action_memory, tag):
    sampled_list = []
    prob_dict = action_memory["conditions"]
    for cond, prob in prob_dict.items():
        if np.random.rand() <= prob:
            sampled_list.append(cond)

    if len(sampled_list) == 0:
        return "", []
    elif tag == "pre":
        return convert_precondition_to_text(sampled_list), sampled_list
    else:
        return convert_postcondition_to_text(sampled_list), sampled_list


class Memory:
    def __init__(self, args, domain):
        self.gamma = args.gamma
        self.save_verbose = args.save_verbose
        self.alpha = args.alpha
        self.previous_trajs = []
        self.sampled_dicts = []
        self.condition_dict = {f"{a}_pre": {"conditions": defaultdict(float), "total": 0} for a in domain.action_name}
        self.condition_dict.update(
            {f"{a}_post": {"conditions": defaultdict(float), "total": 0} for a in domain.action_name}
        )
        self.current_action_desp = ""

    def sample_new_domain_file(self, args, agent, domain, exp_base_folder):
        action_prompt = agent.action_desp_prompt
        action_desp = []
        if os.path.exists(f"{exp_base_folder}/memory.pkl") and not args.rerun:
            self.load_previous_memory(exp_base_folder)
            self.previous_trajs = self.previous_trajs[:-1]
            sampled_dict = self.sampled_dicts[-1]
            for (nl, name, params) in zip(domain.action_nl, domain.action_name, domain.action_params):
                precond_text = convert_precondition_to_text(sampled_dict[f"{name}_pre"])
                postcond_text = convert_postcondition_to_text(sampled_dict[f"{name}_post"])
                action_desp.append(fill_in_action_desp(action_prompt, nl, name, params, precond_text, postcond_text))
        else:
            sampled_dict = defaultdict(list)
            for (nl, name, params) in zip(domain.action_nl, domain.action_name, domain.action_params):
                if self.condition_dict[f"{name}_pre"]["total"] > 0:
                    precond_text, sampled_list = sample_from_memory(self.condition_dict[f"{name}_pre"], "pre")
                    sampled_dict[f"{name}_pre"] = sampled_list
                else:
                    precond_text = ""
                if self.condition_dict[f"{name}_post"]["total"] > 0:
                    postcond_text, sampled_list = sample_from_memory(self.condition_dict[f"{name}_post"], "post")
                    sampled_dict[f"{name}_post"] = sampled_list
                else:
                    postcond_text = ""
                action_desp.append(fill_in_action_desp(action_prompt, nl, name, params, precond_text, postcond_text))

            self.sampled_dicts.append(sampled_dict)
        if self.save_verbose:
            with open(f"{exp_base_folder}/sampled_dict.json", "w") as f:
                json.dump(sampled_dict, f, indent=2)
        self.save_predicted_domain_file(args, domain, exp_base_folder)
        self.current_action_desp = "\n".join(action_desp)

    def update(self, args, domain, cnf_dict, post_actions, pre_actions, exp_base_folder):
        if os.path.exists(f"{exp_base_folder}/memory.pkl") and not args.rerun:
            return
        post_count = Counter(itertools.chain.from_iterable(post_actions))
        pre_count = Counter(itertools.chain.from_iterable(pre_actions))
        executed_bonus = 0  #2
        for tag in ["pre", "post"]:
            for i, a in enumerate(domain.action_name):
                if not ((post_count[a] > 0 and tag == "post") or (pre_count[a] > 0 and tag == "pre")):
                    continue
                count_bonus = executed_bonus * (post_count[a] if tag == "post" else pre_count[a])
                total = len(cnf_dict[f"{a}_{tag}"]) + count_bonus
                self.condition_dict[f"{a}_{tag}"]["total"] += total
                for cond in self.condition_dict[f"{a}_{tag}"]["conditions"]:
                    self.condition_dict[f"{a}_{tag}"]["conditions"][cond] *= self.gamma
                tmp_cond_count = defaultdict(int)
                for j, raw_pred in enumerate(cnf_dict[f"{a}_{tag}"]):
                    lm_pred = "(and" + raw_pred.split("(and")[1].split("\n\n")[0]
                    processed_lm_pred = split_cnf_prediction_by_parentheses(lm_pred)
                    for cond in processed_lm_pred:
                        cond_name = cond.split("?")[0].strip().split("(")[-1].split(")")[0].strip()
                        pred_params = get_params_set(cond)
                        if cond_name in domain.domain_preds and check_params_type(pred_params,
                                                                                  domain.action_params_dict[i],
                                                                                  domain.domain_preds[cond_name]):
                            if (a in post_actions[j] and tag == "post") or (a in pre_actions[j] and tag == "pre"):
                                tmp_cond_count[cond] += (1 + executed_bonus)
                            else:
                                tmp_cond_count[cond] += 1
                f_ratio = self.gamma if (post_count[a] > 0 and tag == "post") or (pre_count[a] > 0 and tag == "pre") else self.alpha
                for cond, count in tmp_cond_count.items():
                    if self.condition_dict[f"{a}_{tag}"]["conditions"][cond] > 0:
                        self.condition_dict[f"{a}_{tag}"]["conditions"][cond] = f_ratio * self.condition_dict[f"{a}_{tag}"]["conditions"][cond] + (1 - f_ratio) * count / total
                    else:
                        self.condition_dict[f"{a}_{tag}"]["conditions"][cond] = count / total
        if self.save_verbose:
            self.save_current_memory(exp_base_folder)

    def save_predicted_domain_file(self, args, domain, exp_base_folder):
        new_domain_file = os.path.join(exp_base_folder, "new_domain.pddl")
        if self.save_verbose and os.path.exists(new_domain_file) and not args.rerun:
            return
        new_domain_pddl = copy.copy(domain.domain_acthead_pddl)
        sampled_dict = self.sampled_dicts[-1]
        for postfix in ["pre", "post"]:
            for a in domain.action_name:
                tag = f"{a}_{postfix}"
                new_domain_pddl = new_domain_pddl.replace(f"[[{tag}]]", "\n".join(sampled_dict[tag]))
        new_domain_file = os.path.join(exp_base_folder, "new_domain.pddl")
        with open(new_domain_file, "w") as f:
            f.write(new_domain_pddl)
        
    def load_previous_memory(self, exp_base_folder):
        self.previous_trajs, self.sampled_dicts, self.condition_dict = pickle.load(
            open(f"{exp_base_folder}/memory.pkl", "rb"))

    def save_current_memory(self, exp_base_folder):
        with open(f"{exp_base_folder}/memory.pkl", "wb") as f:
            pickle.dump((self.previous_trajs, self.sampled_dicts, self.condition_dict), f)


