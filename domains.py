import glob
import itertools
import os
import numpy as np

from collections import defaultdict
from utils import find_all_children, split_cnf_prediction_by_parentheses, \
    state_transition, check_pre_conds_satisfy, parse_pddl_attr_from_string, \
    parse_pddl_type_from_string, parse_pddl_param_list, PARAM_NAME_MATCHES

###############################################################################
#
# Define different problem domains
#
###############################################################################

ALL_DOMAINS = [
    "barman",
    "blocksworld",
    "floortile",
    "grippers",
    "storage",
    "termes",
    "tyreworld",
]


def get_task_type_object_matching(tp, type_dict, task_objs, matching_dict):
    if tp in matching_dict:
        return matching_dict
    if tp not in type_dict or len(type_dict[tp]) == 0:  # leaf node
        if tp not in task_objs:
            print(f"{tp} type has no object in the task.")
            matching_dict[tp] = []
        else:
            matching_dict[tp] = task_objs[tp]
    else:
        matching_dict[tp] = []
        for child_type in type_dict[tp]:
            matching_dict = get_task_type_object_matching(child_type, type_dict, task_objs, matching_dict)
            matching_dict[tp] += matching_dict[child_type]
    return matching_dict


class Domain:
    def __init__(self, name):
        # every domain should contain the context as in "in-context learning" (ICL)
        # which are the example problem in natural language.
        # For instance, in our case, context is:
        # 1. p_example.nl  (a language description of the problem)
        # 2. p_example.pddl (the ground-truth problem pddl for the problem)
        # 3. p_example.sol  (the ground-truth solution in natural language to the problem)
        self.name = name

        # IC example files
        self.example_files = ("p_example.nl", "p_example.pddl", "p_example.sol_pddl")
        self.examples = self.get_context()
        self.example_init = parse_pddl_attr_from_string(self.examples[1], attr_starter="(:init")[1]

        # Domain files
        self.domain_nl, self.domain_pddl = self.get_domain()
        self.domain_types, self.has_type, domain_type_str = self.get_domain_type()
        self.domain_preds, domain_pred_str = self.get_domain_predicate()
        self.domain_type_pred_str = domain_type_str + domain_pred_str
        self.action_name, self.action_params, self.action_params_dict, self.action_nl, self.domain_acthead_pddl = \
            self.get_domain_action()
        self.raw_action_desp = "\n".join([f"{nl}: {name} {params}." for nl, name, params in
                                          zip(self.action_nl, self.action_name, self.action_params)])

        # Task files
        self.task_files = self.grab_tasks()  # should be list of tuples like (descritpion, ground_truth_pddl)
        self.tasks_nl, self.tasks_pddl = [self.get_task(i)[0] for i in range(len(self.task_files))], [
            self.get_task(i)[1] for i in range(len(self.task_files))]
        self.task_init_state = [parse_pddl_attr_from_string(task_pddl, attr_starter="(:init")[1]
                                for task_pddl in self.tasks_pddl]
        task_objects = [parse_pddl_type_from_string(task_pddl, type_starter="(:objects")[1]
                        for task_pddl in self.tasks_pddl]
        self.task_type_object_matching = []
        for task_objects in task_objects:
            matching_dict = {}
            for tp in self.domain_types:
                matching_dict = get_task_type_object_matching(tp, self.domain_types, task_objects, matching_dict)
            matching_dict = {k: list(set(v)) for k, v in matching_dict.items()}
            self.task_type_object_matching.append(matching_dict)

    def __len__(self):
        return len(self.task_files)

    def get_domain_nl_file(self):
        return f"./domains/{self.name}/domain.nl"

    def get_domain_pddl_file(self):
        return f"./domains/{self.name}/domain.pddl"

    def get_domain_valid_pddl_file(self):
        if os.path.exists(f"./domains/{self.name}/domain_validation.pddl"):
            return f"./domains/{self.name}/domain_validation.pddl"
        else:
            return f"./domains/{self.name}/domain.pddl"

    def get_domain(self):
        domain_nl_f = self.get_domain_nl_file()
        domain_pddl_f = self.get_domain_pddl_file()
        try:
            with open(domain_nl_f, "r") as f:
                domain_nl = f.read()
        except:
            domain_nl = "Nothing"
        with open(domain_pddl_f, "r") as f:
            domain_pddl = f.read()
        return domain_nl.strip(), domain_pddl.strip()

    def get_domain_type(self):
        if "(:types" in self.domain_pddl:
            type_strs, pddl_types = parse_pddl_type_from_string(self.domain_pddl, type_starter="(:types")
            type_strs = "\n".join([s.strip() for s in type_strs.splitlines()])
            domain_type_str = f"PDDL Types:\n{type_strs}\n"
            if "" not in pddl_types:  # add dummy node
                pddl_types[""] = list(pddl_types.keys())
            return pddl_types, True, domain_type_str
        else:
            return {"": []}, False, ""

    def get_domain_predicate(self):
        assert "(:predicates" in self.domain_pddl
        full_pred_str, preds_strs = parse_pddl_attr_from_string(self.domain_pddl, attr_starter="(:predicates")
        pddl_preds = {}
        domain_pred_str = "PDDL Predicates:\n"
        for preds_str in preds_strs:
            pred_name, params_dict = parse_pddl_param_list(preds_str)
            pddl_preds[pred_name] = []
            for p_name, p_type in params_dict.items():
                if isinstance(p_type, list):
                    pddl_preds[pred_name].append(set())
                    for sub_type in p_type:
                        pddl_preds[pred_name][-1] = pddl_preds[pred_name][-1].union(
                            find_all_children(sub_type, self.domain_types))
                else:
                    pddl_preds[pred_name].append(find_all_children(p_type, self.domain_types))
            domain_pred_str += f"{preds_str.strip()}\n"
        return pddl_preds, domain_pred_str

    def get_domain_action(self):
        action_pddl_str_list, all_actions = parse_pddl_attr_from_string(self.domain_pddl, attr_starter="(:action")
        action_name, action_params, action_params_dict = [], [], []
        acthead_pddl = self.domain_pddl
        for action_pddl_str, (name, action_attr) in zip(action_pddl_str_list, all_actions.items()):
            assert len(action_attr) == 3
            param_str, pre_cond_str, post_cond_str = action_attr
            action_name.append(name)
            action_params.append(param_str)
            action_params_dict.append(parse_pddl_param_list(param_str)[1])
            new_action_pddl_str = f"(:action {name}\n\t:parameters {param_str}\n\t:precondition (and [[{name}_pre]])" \
                                  f"\n\t:effect (and [[{name}_post]]))"
            acthead_pddl = acthead_pddl.replace(action_pddl_str, new_action_pddl_str)
        action_nl = open(f"./domains/{self.name}/actions.nl").read().splitlines()
        assert len(action_name) == len(action_nl)
        return action_name, action_params, action_params_dict, action_nl, acthead_pddl

    def grab_tasks(self):
        path = f"./domains/{self.name}"
        nls = []
        for fn in glob.glob(f"{path}/*.nl"):
            fn_ = fn.split("/")[-1]
            if "domain" not in fn_ and "p_example" not in fn_:
                if os.path.exists(fn.replace("nl", "pddl")):
                    nls.append(fn_)
        sorted_nls = sorted(nls)
        return [(nl, nl.replace("nl", "pddl")) for nl in sorted_nls]

    def get_context(self):
        nl_f = f"./domains/{self.name}/{self.example_files[0]}"
        pddl_f = f"./domains/{self.name}/{self.example_files[1]}"
        sol_f = f"./domains/{self.name}/{self.example_files[2]}"
        with open(nl_f, "r") as f:
            nl = f.read()
        with open(pddl_f, "r") as f:
            pddl = f.read()
        with open(sol_f, "r") as f:
            sol = f.read()
        return nl.strip(), pddl.strip(), sol.strip()

    def get_task_file(self, i):
        nl, pddl = self.task_files[i]
        return f"./domains/{self.name}/{nl}", f"./domains/{self.name}/{pddl}"

    def get_task(self, i):
        nl_f, pddl_f = self.get_task_file(i)
        with open(nl_f, "r") as f:
            nl = f.read()
        with open(pddl_f, "r") as f:
            pddl = f.read()
        return nl.strip(), pddl.strip()

    def get_task_one_random_action(self, i):
        rand_index = np.random.choice(range(len(self.action_name)))
        rand_a_name = self.action_name[rand_index]
        rand_params = []
        for p_name, p_type in self.action_params_dict[rand_index].items():
            rand_params.append(np.random.choice(self.task_type_object_matching[i][p_type]))
        return f"({rand_a_name} {' '.join(rand_params)})"

    def get_task_one_explored_action(self, i, current_state, memory):
        cond_dict = memory.sampled_dicts[-1]
        action_indices = list(range(len(self.action_name)))
        task_objects = self.task_type_object_matching[i]
        while True:
            rand_index = np.random.choice(action_indices)
            a_name = self.action_name[rand_index]
            pre_conds = sorted(cond_dict[f"{a_name}_pre"], key=lambda x: len(x.split("?")))
            a_param_obj_map = {param_name: task_objects[param_type] for param_name, param_type in
                               self.action_params_dict[rand_index].items()}

            checking_params = list(set(
                itertools.chain.from_iterable(PARAM_NAME_MATCHES.findall(cond) for cond in pre_conds)
            ))
            checking_objs = [a_param_obj_map[param_name] for param_name in checking_params]
            for objs in itertools.product(*checking_objs):
                param_to_obj = {p: obj for p, obj in zip(checking_params, objs)}
                if check_pre_conds_satisfy(current_state, pre_conds, param_to_obj):
                    explored_params = []
                    for p_name, p_type in self.action_params_dict[rand_index].items():
                        if p_name in param_to_obj:
                            explored_params.append(param_to_obj[p_name])
                        else:
                            rand_obj = np.random.choice(task_objects[p_type])
                            explored_params.append(rand_obj)
                            param_to_obj[p_name] = rand_obj
                    return f"({a_name} {' '.join(explored_params)})", \
                        state_transition(current_state, cond_dict[f"{a_name}_post"], param_to_obj)
            action_indices.remove(rand_index)
            if len(action_indices) == 0:
                print("Dead End. Turn to random generator.")
                return self.get_task_one_random_action(i), None

    def parse_gt_pre_post_cond(self):
        domain_valid_pddl_f = self.get_domain_valid_pddl_file()
        with open(domain_valid_pddl_f, "r") as f:
            domain_valid_pddl = f.read().strip()
        cond_dict = {}
        for a in self.action_name:
            act_str = domain_valid_pddl.split(f"(:action {a}")[1]
            for postfix in ["pre", "post"]:
                split_tag = ":precondition" if postfix == "pre" else ":effect"
                cond_str = act_str.split(split_tag)[1].strip()
                if cond_str.startswith("(and"):
                    cond_dict[f"{a}_{postfix}"] = split_cnf_prediction_by_parentheses(cond_str)
                else:
                    cond_dict[f"{a}_{postfix}"] = {cond_str.split(")")[0].strip() + ")"}
                cond_dict[f"{a}_{postfix}"] = set(sorted(list(cond_dict[f"{a}_{postfix}"]),
                                                     key=lambda x: 0 if x.startswith("(not ") else 1))
        return cond_dict
