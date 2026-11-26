"""Overlay the validation curves of several training runs on one plot.

Reads runs/pose/<name>/results.csv for each run name and plots box mAP50
and box mAP50-95 per epoch, smoothed over a few epochs so the trend is visible.

Usage (from the training/ folder):
    python3 plot_runs.py aug1 aug2
    python3 plot_runs.py aug1 aug2 --smooth 1      # no smoothing
Saves figures/compare_<names>.png
"""

import argparse
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")                     # draw to a file, no window needed
import matplotlib.pyplot as plt

RUNS_DIR = Path("runs/pose")
FIG_DIR = Path("figures")


def read_results(run_name):
    """Return (epochs, {column name: list of values}) from one run's results.csv."""
    path = RUNS_DIR / run_name / "results.csv"
    with open(path) as f:
        rows = list(csv.DictReader(f))
    epochs = [int(r["epoch"]) for r in rows]
    columns = {key: [float(r[key]) for r in rows] for key in rows[0] if key != "epoch"}
    return epochs, columns


def moving_average(values, window):
    """Average each value with the (window - 1) values before it."""
    out = []
    for i in range(len(values)):
        chunk = values[max(0, i - window + 1): i + 1]
        out.append(sum(chunk) / len(chunk))
    return out


def main():
    parser = argparse.ArgumentParser(description="Compare training runs.")
    parser.add_argument("runs", nargs="+", help="run names, e.g. aug1 aug2")
    parser.add_argument("--smooth", type=int, default=10, help="epochs to average over")
    args = parser.parse_args()

    fig, ax = plt.subplots(figsize=(9, 4))
    for run in args.runs:
        epochs, cols = read_results(run)
        line, = ax.plot(epochs, moving_average(cols["metrics/mAP50-95(B)"], args.smooth),
                        label=f"{run}: box mAP50-95")
        ax.plot(epochs, moving_average(cols["metrics/mAP50(B)"], args.smooth),
                ls="--", color=line.get_color(), label=f"{run}: box mAP50")

    ax.set_xlabel("epoch")
    ax.set_ylabel(f"validation score ({args.smooth}-epoch average)")
    ax.set_ylim(0, 1)
    ax.set_title(" vs ".join(args.runs))
    ax.legend(fontsize=8, loc="lower right")
    FIG_DIR.mkdir(exist_ok=True)
    out = FIG_DIR / f"compare_{'_'.join(args.runs)}.png"
    fig.tight_layout()
    fig.savefig(out, dpi=110)
    print(f"saved {out}")


if __name__ == "__main__":
    main()
