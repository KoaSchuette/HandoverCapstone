"""Plot pickup -> handover time against pegboard offset (exp-001).

Reads the raw study data from cycle_times.csv at the repo root and saves
time_vs_offset.png next to this script. Run from anywhere:

    python3 plot_times.py
"""
import csv
from pathlib import Path

import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
CSV = HERE.parents[3] / "cycle_times.csv"     # repo root
OUT = HERE / "time_vs_offset.png"

# Predicted handover times (s) from the PTP timing model, made before the runs.
PREDICTED = {-0.05: 3.14, 0.00: 3.47, 0.05: 3.64, 0.10: 3.74, 0.15: 3.82}
REACH_LIMIT = -0.075   # m, set by the UR5e wrist offset (d4 = 0.133 m)
CAD_ARM_MM = 405       # arm length at offset 0 in the CAD
START = -0.055         # m, chosen start position (35 cm arms)

# Measured handover times: successful 'handover' rows only
measured = {}
with open(CSV, newline="") as f:
    for row in csv.DictReader(f):
        if row["leg"] == "handover" and row["status"] == "SUCCESS":
            measured[float(row["offset_m"])] = float(row["time_s"])

offsets = sorted(measured)
fig, ax = plt.subplots(figsize=(7, 4.5))

ax.plot(offsets, [measured[o] for o in offsets], "o-", label="Measured (sim)")
ax.plot(list(PREDICTED), list(PREDICTED.values()), "x--", label="Predicted (model)")
ax.axvspan(-0.11, REACH_LIMIT, color="grey", alpha=0.2)
ax.axvline(REACH_LIMIT, color="grey", linestyle=":")
ax.text(REACH_LIMIT - 0.003, 3.25, "pickup\nunreachable", ha="right", color="dimgrey")
ax.axvline(START, color="green", linestyle="--", linewidth=1)
ax.text(START + 0.003, 3.75, "build start\n(35 cm arms)", color="green")

ax.set_xlim(-0.11, 0.17)
ax.set_xlabel("Pegboard offset from CAD position (m), positive = further from robot")
ax.set_ylabel("Pickup → handover time (s)")
ax.set_title("Pickup → handover time vs pegboard offset\n(Pilz PTP, 30% speed, Gazebo sim)")
ax.grid(alpha=0.3)
ax.legend(loc="lower right")

# Second x-axis: the arm length that gives each offset
arm = ax.secondary_xaxis("top", functions=(lambda x: CAD_ARM_MM + 1000 * x,
                                           lambda mm: (mm - CAD_ARM_MM) / 1000))
arm.set_xlabel("Arm length (mm)")

fig.tight_layout()
fig.savefig(OUT, dpi=200)
print(f"Saved {OUT}")
