# Handover references

## Papers

| Ref | Citation | Used for |
|---|---|---|
| Biagi 2026 | F. Biagi, D. Onfiani, S. Silenzi, C. Iani, L. Biagiotti, "Adaptive vs. Static Robot-to-Human Handover: A Study on Orientation and Approach Direction," arXiv:2604.22378 [cs.RO], Apr. 2026. Project page: https://autolabmodena.github.io/adaptive-human-handover/ | Bézier path, quintic time law, SLERP with orientation lock, approach along the palm; user study results backing the adaptive approach |
| Käppler 2023 | M. Käppler, I. Mamaev, H. Alagi, T. Stein, B. Deml, "Optimizing human-robot handovers: the impact of adaptive transport methods," *Frontiers in Robotics and AI*, vol. 10, 2023. (Cited in Biagi 2026; not read directly yet) | Risk that continuous hand tracking lowers trust and perceived safety |
| Biagiotti 2008 | L. Biagiotti, C. Melchiorri, *Trajectory Planning for Automatic Machines and Robots*. Springer, 2008. (Cited in Biagi 2026) | Bézier curves and polynomial time laws |

## Datasheets and documentation

| Ref | Source | Used for |
|---|---|---|
| UR5e datasheet | Universal Robots. https://www.crossco.com/wp-content/uploads/2024/04/UR5e-Datasheet.pdf | Joint speed limit 180°/s for all joints; reach 850 mm |
| UR5e datasheet (force sensing) | Universal Robots. https://cdn.elmark.com.pl/34833 | Tool flange force sensor range ±50 N, precision ±3.5 N, accuracy ±4.0 N |
| MoveIt `GetPositionIK` | `moveit_msgs/srv/GetPositionIK` | IK service used per sample |
| Ultraleap LeapC Python bindings | https://github.com/ultraleap/leapc-python-bindings | Hand data source for `leap_node` |

[TBD: add the Leap Motion Controller 2 datasheet, and save a PDF copy of the Biagi paper here.]
