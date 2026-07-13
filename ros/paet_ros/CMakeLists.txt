cmake_minimum_required(VERSION 3.0.2)
project(paet_ros)

find_package(catkin REQUIRED COMPONENTS
  actionlib_msgs
  geometry_msgs
  message_generation
  nav_msgs
  rospy
  sensor_msgs
  std_msgs
  tf2_ros
  visualization_msgs
)

add_message_files(
  FILES
  PAETEvent.msg
  PAETEventArray.msg
)

generate_messages(
  DEPENDENCIES
  geometry_msgs
  std_msgs
)

catkin_package(
  CATKIN_DEPENDS
    actionlib_msgs
    geometry_msgs
    message_runtime
    nav_msgs
    rospy
    sensor_msgs
    std_msgs
    tf2_ros
    visualization_msgs
)

catkin_install_python(PROGRAMS
  scripts/paet_geometry_tokenizer.py
  scripts/paet_event_logger.py
  scripts/paet_eval_helper.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)

install(DIRECTORY config launch
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)

