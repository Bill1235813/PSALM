import matplotlib.pyplot as plt
import os
import json

metric = {"precision": "overall precision", "weighted_precision": "overall precision weighted",
          "recall": "overall recall", "weighted_recall": "overall recall weighted"}


def plot_metrics(exp_base_dir, domain_name, metric, runs=None):
    # Data
    eval_results = json.load(open(f"{exp_base_dir}/metrics.json"))
    # y_values = [0.84, 0.85, 0.88, 0.90, 0.91, 0.91, 0.90, 0.91, 0.94, 0.94, 0.95, 0.96, 0.96, 0.97, 0.97, 0.98, 0.98, 0.98, 0.98, 0.99, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    # y_values = [0.55, 0.57, 0.58, 0.59, 0.58, 0.621, 0.634, 0.67, 0.66, 0.68, 0.71, 0.74, 0.76, 0.78, 0.78, 0.76, 0.77, 0.75, 0.795, 0.82, 0.816, 0.83, 0.84, 0.85, 0.88, 0.90, 0.913, 0.923, 0.94]

    for m_name in metric:
        y_values = eval_results[m_name]
        if runs is not None:
            x_values = list(range(1, runs + 1))
        else:
            x_values = list(range(1, len(y_values) + 1))
        # y_values = [0.88, 0.84, 0.82, 0.81, 0.83, 0.81, 0.844, 0.83, 0.86, 0.88, 0.867, 0.889, 0.895, 0.874, 0.881, 0.904, 0.915, 0.920, 0.928, 0.928, 0.940, 0.952, 0.952, 0.955, 0.958, 0.960, 0.963, 0.963, 0.97]

        # Plot
        plt.figure()
        plt.plot(x_values, y_values, marker='o', markersize='1', color='b')

        # Title and labels
        plt.title(f'{m_name} vs. Run')
        plt.xlabel('Run')
        plt.ylabel(m_name)

        # Customize axes range
        # plt.xticks(range(1, runs + 1, 4))
        # plt.ylim(0.84, 1.05)

        # Show plot
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(f"{exp_base_dir}/{m_name}_{domain_name}.jpeg")
        # plt.show()

if __name__ == "__main__":
    exp_base_dir = "./experiments/debug8/rand_rule_based/grippers/"
    domain_name = "grippers"
    runs = 999
    plot_metrics(exp_base_dir, domain_name, metric, runs)