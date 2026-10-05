# custom msg contain all information on hand
std_msgs/Header header

float32 confidence

uint8 LEFT=0
uint8 RIGHT=1
uint8 handedness

float32 grab_strength
float32 pinch_strength

geometry_msgs/Vector3 palm_normal
geometry_msgs/Vector3 palm_velocity
geometry_msgs/Vector3 palm_direction
float32 width

geometry_msgs/Pose palm
geometry_msgs/Point wrist_joint
geometry_msgs/Point elbow_joint

# order of fingers are thumb, index, middle, ring, pinky
Finger[5] fingers



