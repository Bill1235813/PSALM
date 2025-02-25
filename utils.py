import numpy as np
import re

from collections import defaultdict

PARAM_LIST_MATCHER = re.compile("((?:\?\S+\s*)+)(?:-\s+([^\?$]+)\s*)?")
PARAM_NAME_MATCHES = re.compile("\?([^\s\?\)]+)\s*")


def parse_pddl_param_list(s):
    s = s.strip()
    assert s[0] == "(" and s[-1] == ")"
    s = s[1:-1]
    param_type_dict = {}
    for params, p_type in PARAM_LIST_MATCHER.findall(s):
        for p in PARAM_NAME_MATCHES.findall(params):
            p_type = p_type.strip()
            if p_type.startswith("("):
                p_type = p_type[1:-1].strip()
                assert "either"
                param_type_dict[p] = re.split("\s+", p_type)[1:]
            else:
                param_type_dict[p] = p_type
    return s.split("?")[0].strip(), param_type_dict


def parse_outer_inner_str(s, str_ender, inner_starter, inner_ender):
    inner_count = 0
    start_id = 0
    matched_str = []
    for i, c in enumerate(s):
        if inner_count == 0 and c == str_ender:
            return s[:i + 1], matched_str, i + 1
        elif c == inner_starter:
            if inner_count == 0:
                start_id = i
            inner_count += 1
        elif c == inner_ender:
            inner_count -= 1
            if inner_count == 0:
                matched_str.append(s[start_id:i + 1])
    return s, matched_str, len(s)


def parse_pddl_attr_from_string(s, attr_starter="(:", attr_ender=")", inner_starter="(", inner_ender=")",
                                overlap=False):
    s_attr = s.split(attr_starter)
    if len(s_attr) == 1:
        return "", []
    elif len(s_attr) == 2:
        outer_str, inner_str, _ = parse_outer_inner_str(s_attr[1], attr_ender, inner_starter, inner_ender)
        return attr_starter + outer_str, inner_str
    else:
        matched_dict = {}
        outer_list = []
        if not overlap:
            while len(s.split(attr_starter)) > 1:
                s = s.split(attr_starter, 1)[1]
                name = re.split("\s+", s.strip())[0]
                outer_str, inner_str, end_point = parse_outer_inner_str(s, attr_ender, inner_starter, inner_ender)
                outer_list.append(attr_starter + outer_str)
                matched_dict[name] = inner_str
                s = s[end_point:]
        else:
            for seg in s_attr[1:]:
                name = re.split("\s+", seg.strip())[0]
                outer_str, inner_str, _ = parse_outer_inner_str(seg, attr_ender, inner_starter, inner_ender)
                outer_list.append(attr_starter + outer_str)
                matched_dict[name] = inner_str
        return outer_list, matched_dict


def parse_pddl_type_from_string(s, type_starter="(:", type_ender=")", separator=" - "):
    def pairwise(iterable):
        a = iter(iterable)
        return zip(a, a)

    s_type = s.split(type_starter)
    if len(s_type) == 1:
        return "", []
    elif len(s_type) == 2:
        s_type = s_type[1].split(type_ender)[0].strip()
        type_strs = re.split(separator + "(\S+)", s_type)
        type_dict = defaultdict(list)
        if len(type_strs) > 1:
            assert len(type_strs) % 2 == 1
            for child_str, parent in pairwise(type_strs[:-1]):
                children = re.split("\s+", child_str.strip())
                type_dict[parent] += children
        else:
            parents = re.split("\s+", type_strs[0].strip())
            type_dict[""] += parents
        return s_type, type_dict
    else:
        raise ValueError(f"{type_starter} occurs more than one time.")


def set_seed(seed):
    np.random.seed(seed)


def clean_trajectory_from_val(s):
    assert s.startswith("Plan size: ")
    size = int(s.split("\n")[0].split("Plan size: ")[1])
    plan_and_vals = []
    actions = []
    plans = []
    if size > 0:
        plan_str = s.split("\n", 1)[1].split("Plan Validation details")[0]
        plan_val_str = s.split("Plan Validation details")[1]\
            .split("Failed plans:")[0]\
            .split("Plan executed successfully")[0]\
            .split("\n\n", 1)[1]
        plan_val_list = plan_val_str.split("\n\n")

        for i, plan_val in enumerate(plan_val_list):
            if plan_val.startswith("Checking"):
                plan = plan_str.split(f"{i + 1}:")[1].split("\n \n")[0].strip()
                action = plan.split()[0][1:]
                plan_and_vals.append(f"{plan}\n{plan_val}")
                plans.append(plan)
                actions.append(action)
            else:
                plan_and_vals[-1] += "\n".join(plan_val_list[i:])
                break
    return plan_and_vals, plans, actions


def remove_type_in_cnf(s):
    s_split_type = s.split(" - ")
    if len(s_split_type) > 1:
        for i in range(1, len(s_split_type)):
            if len(s_split_type[i].strip().split(")")[0].split()) == 1:
                s_split_type[i] = ")" + s_split_type[i].strip().split(")", 1)[1]
            else:
                s_split_type[i] = " " + s_split_type[i].strip().split(" ", 1)[1]
        return "".join(s_split_type).strip()
    else:
        return s


def split_cnf_prediction_by_parentheses(s):
    assert s.startswith("(and")
    matches = set()
    p_count = 0
    clause_start_id = 0
    for i in range(len(s)):
        if s[i] == "(":
            p_count += 1
            if p_count == 2:
                clause_start_id = i
        elif s[i] == ")":
            p_count -= 1
            if p_count == 0:
                break
            elif p_count == 1:
                matches.add(remove_type_in_cnf(s[clause_start_id:i + 1]))
    return matches


def check_params_type(pred_params, gt_params_type, gt_preds_type):
    if len(pred_params) != len(gt_preds_type):
        return False
    for i, p in enumerate(pred_params):
        if p not in gt_params_type:
            return False
        if gt_params_type[p] not in gt_preds_type[i]:
            return False
    return True


def get_params_set(s):
    params = s.split("?")[1:]
    short_params = []
    for p in params:
        short_params.append(p.split(")")[0].split(" ")[0])
    return short_params


def find_all_children(parent, child_dict):
    if parent not in child_dict:
        return {parent}
    else:
        children_set = {parent}
        for child in child_dict[parent]:
            children_set = children_set.union(find_all_children(child, child_dict))
        return children_set


def check_any_prefix_plans(plan, failed_plans):
    plan_str = "\n".join(plan)
    failed_plans_str = ["\n".join(fp[0]) for fp in failed_plans]
    for fp_str in failed_plans_str:
        if plan_str.startswith(fp_str):
            return True
    return False


def construct_param_to_obj(domain, action):
    action = action[1:-1]
    a_name = action.split(" ")[0].strip()
    objs = action.split(" ")[1:]
    a_index = domain.action_name.index(a_name)
    assert len(objs) == len(domain.action_params_dict[a_index])
    return {p: obj for p, obj in zip(domain.action_params_dict[a_index], objs)}, a_name


def state_transition(current_state, effects, param_to_obj):
    for obj_cond in effects:
        for param in param_to_obj:
            obj_cond = re.sub(r"\?{}(?=[^\w-])".format(param), param_to_obj[param], obj_cond)
        _, reversed_cond = parse_pddl_attr_from_string(obj_cond, attr_starter="(not ")
        if reversed_cond:
            assert len(reversed_cond) == 1
            if reversed_cond[0] in current_state:
                current_state.remove(reversed_cond[0])
        elif obj_cond.strip() not in current_state:
            current_state.append(obj_cond)
    return current_state


def check_pre_conds_satisfy(current_state, pre_conds, param_to_obj):
    for obj_cond in pre_conds:
        for param in param_to_obj:
            obj_cond = re.sub(r"\?{}(?=[^\w-])".format(param), param_to_obj[param], obj_cond)
        if (obj_cond.startswith("(not ") and obj_cond in current_state) or \
                (not obj_cond.startswith("(not ") and obj_cond not in current_state):
            return False
    return True


# leave for later
def search_satisfying_param(current_state, pre_conds, a_param_obj_map):
    for cond in pre_conds:
        params = [p.strip() for p in cond[1:-1].split("?")[1:]]
