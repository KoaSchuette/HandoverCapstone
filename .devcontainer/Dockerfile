FROM osrf/ros:jazzy-desktop-full

RUN apt-get update && apt-get install -y \
    python3-colcon-common-extensions \
    python3-rosdep \
    python3-pip \
    python3-dev \
    git \
    sudo \
    mesa-utils \
    usbutils \
    ros-jazzy-ur \
    ros-jazzy-ur-simulation-gz \
    ros-jazzy-realsense2-camera \
    ros-jazzy-realsense2-description \
    ros-jazzy-rqt-image-view \
    && rm -rf /var/lib/apt/lists/*

# Pip-only Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip install --break-system-packages -r /tmp/requirements.txt

# Ubuntu 24.04 images already have a user "ubuntu" with UID 1000; reuse it
RUN echo "ubuntu ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/ubuntu \
    && chmod 0440 /etc/sudoers.d/ubuntu

USER ubuntu
RUN rosdep update
RUN echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc