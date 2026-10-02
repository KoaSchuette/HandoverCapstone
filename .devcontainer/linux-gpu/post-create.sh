set -e

sudo apt-get update
rosdep install --from-paths src --ignore-src -y

pip install --break-system-packages \
  "git+https://github.com/ultraleap/leapc-python-bindings.git#subdirectory=leapc-cffi"
pip install --break-system-packages \
  "git+https://github.com/ultraleap/leapc-python-bindings.git#subdirectory=leapc-python-api"