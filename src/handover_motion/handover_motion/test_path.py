import numpy as np
import matplotlib.pyplot as plt

from helper import time_law, bezier, find_pull_points

# Test inputs (z = 0 so we can plot in 2D)
p_0 = np.array([0.0, 0.0, 0.0])   # start (rack)
p_3 = np.array([1.0, 1.0, 0.0])   # end (hand)
d_a = np.array([1.0, 0.0, 0.0])   # leave heading +x
d_s = np.array([0.0, 1.0, 0.0])   # arrive heading +y (direction of travel into the hand)
a_s = 0.1
a_a = 0.1

points = find_pull_points(p_0, p_3, d_s, d_a, a_s, a_a)

# Plot 1: the curve shape, evenly spaced s
s_values = np.linspace(0, 1, 50)
curve = np.array([bezier(points, s) for s in s_values])

# Plot 2: time law + Bezier, evenly spaced time
duration = 2.0
times = np.linspace(0, duration, 30)
timed = np.array([bezier(points, time_law(t, duration)) for t in times])

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5))

ax1.plot(curve[:, 0], curve[:, 1], label='Bezier curve')
ax1.scatter(points[:, 0], points[:, 1], color='red', zorder=3, label='control points')
for i, p in enumerate(points):
    ax1.annotate(f'p{i}', (p[0], p[1]), textcoords='offset points', xytext=(6, 6))
ax1.set_title('Path shape')
ax1.axis('equal')
ax1.legend()

ax2.plot(curve[:, 0], curve[:, 1], color='lightgray')
ax2.scatter(timed[:, 0], timed[:, 1], s=15, label='position every 0.07 s')
ax2.set_title('Path + time law (dot spacing = speed)')
ax2.axis('equal')
ax2.legend()

plt.tight_layout()
plt.show()