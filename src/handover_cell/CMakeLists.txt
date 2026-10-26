cmake_minimum_required(VERSION 3.8)
project(handover_cell)

find_package(ament_cmake REQUIRED)

# Nothing to compile: just copy the data folders into install/share/handover_cell
install(DIRECTORY launch meshes srdf urdf
  DESTINATION share/${PROJECT_NAME})

install(PROGRAMS
  scripts/handover_demo.py
  DESTINATION lib/${PROJECT_NAME})

ament_package()
