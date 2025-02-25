import itertools
import json

###############################################################################
#
# The evaluator of the learning proces of various methods
#
###############################################################################

METRICS = ["precision", "recall",
           "weighted_precision", "weighted_recall",
           "threshold_precision", "threshold_recall"]


class Evaluator:
    def __init__(self, args, domain, threshold=0.5):
        self.action_name = domain.action_name
        self.gt_cond_dict = domain.parse_gt_pre_post_cond()
        self.overall_gt = len(list(itertools.chain.from_iterable(self.gt_cond_dict.values())))
        self.overall_steps = 0
        self.save_verbose = args.save_verbose
        self.threshold = threshold
        self.metrics_dict = {}
        for metric in METRICS:
            self.metrics_dict[metric] = []

    def eval_score(self, condition_dict, exp_base_folder):
        overall_acc, overall_acc_thres, overall_acc_weighted = 0, 0, 0
        overall_pred, overall_pred_thres, overall_pred_weighted = 0, 0, 0
        log_str = ""
        for tag in ["pre", "post"]:
            for a in self.action_name:
                a_tag = f"{a}_{tag}"
                lm_pred = set(condition_dict[a_tag]["conditions"].keys())
                lm_pred_thres = set([k for k in condition_dict[a_tag]["conditions"].keys() if
                                     condition_dict[a_tag]["conditions"][k] >= self.threshold])
                lm_weighted_sum = sum(condition_dict[a_tag]["conditions"].values())
                acc = len(self.gt_cond_dict[a_tag].intersection(lm_pred))
                acc_thres = len(self.gt_cond_dict[a_tag].intersection(lm_pred_thres))
                acc_weighted = sum([condition_dict[a_tag]["conditions"][cond] for cond in
                                    self.gt_cond_dict[a_tag].intersection(lm_pred)])
                overall_acc += acc
                overall_acc_thres += acc_thres
                overall_acc_weighted += acc_weighted
                overall_pred += len(lm_pred)
                overall_pred_thres += len(lm_pred_thres)
                overall_pred_weighted += lm_weighted_sum
                log_str += f"{a_tag}: precision: {acc}/{len(lm_pred)}, recall:{acc}/{len(self.gt_cond_dict[a_tag])} \n" \
                           f"{a_tag}: weighted precision: {acc_weighted:.{2}f}/{lm_weighted_sum:.{2}f}, " \
                           f"recall:{acc_weighted:.{2}f}/{len(self.gt_cond_dict[a_tag])} \n"

        overall_precision = overall_acc / overall_pred if overall_pred > 0 else 0
        overall_threshold_precision = overall_acc_thres / overall_pred_thres if overall_pred_thres > 0 else 0
        overall_weighted_precision = overall_acc_weighted / overall_pred_weighted if overall_pred_weighted > 0 else 0
        overall_recall = overall_acc / self.overall_gt
        overall_threshold_recall = overall_acc_thres / self.overall_gt
        overall_weighted_recall = overall_acc_weighted / self.overall_gt
        for metric in METRICS:
            self.metrics_dict[metric].append(eval(f"overall_{metric}"))

        if self.save_verbose:
            log_str += f"\noverall precision: {overall_precision}, " \
                       f"overall recall: {overall_recall}, " \
                       f"overall precision threshold: {overall_threshold_precision}, " \
                       f"overall recall threshold: {overall_threshold_recall}, " \
                       f"overall precision weighted: {overall_weighted_precision}, " \
                       f"overall recall weighted: {overall_weighted_recall}\n"
            output_eval_file = f"{exp_base_folder}/eval.txt"
            with open(output_eval_file, "w") as f:
                f.write(log_str)

        print(f"overall precision: {overall_precision}, "
              f"overall recall: {overall_recall}, "
              f"overall precision threshold: {overall_threshold_precision}, "
              f"overall recall threshold: {overall_threshold_recall}, "
              f"overall precision weighted: {overall_weighted_precision}, "
              f"overall recall weighted: {overall_weighted_recall}")

    def save_metrics(self, exp_base_folder):
        with open(f"{exp_base_folder}/metrics.json", "w") as f:
            json.dump(self.metrics_dict, f)
