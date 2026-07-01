# Robot System Report

Generated: 2026-07-01 16:30 CST
Runtime ROS refresh: 2026-07-01, after navigation stack startup

This report records the robot system state relevant to PAET platform reproducibility. It is a sanitized summary: no raw sensor data, log excerpts, credentials, Wi-Fi details, remote-access secrets, MAC addresses, SSH material, shell history, or full private IP addresses are included.

## Executive Summary

- The machine runs Ubuntu 20.04.6 LTS with ROS 1 Noetic.
- The robot software is organized around `/home/robot/catkin_ws` plus a separate Cartographer workspace at `/home/robot/cartographer`.
- The installed ROS stack includes ROS desktop/full, navigation, perception, image pipeline, PCL, Gazebo, Apriltag, RealSense, and custom robot driver packages.
- The active ROS environment points to `ROS_MASTER_URI=http://localhost:11311`. It was not reachable from the sandbox namespace, but was reachable from the host namespace after ROS startup.
- Navigation uses Cartographer localization/mapping, `move_base`, TEB local planning, global planning, layered costmaps, virtual walls, scan ICP matching, and multi-lidar scan fusion.
- Sensitive local operator notes were present and were excluded from the generated repository files.

## Host and OS

| Field | Value |
| --- | --- |
| Distribution | Ubuntu 20.04.6 LTS |
| Codename | focal |
| Kernel | 5.15.0-139-generic |
| Architecture | x86_64 |
| CPU threads | 20 |
| Memory | 15 GiB RAM |
| Swap | 2 GiB |
| Root filesystem | 938 GiB total, about 845 GiB available during collection |

`hostnamectl` could not be queried in the sandbox because system bus access was not permitted. The kernel hostname was intentionally not reproduced verbatim.

## ROS Environment

| Field | Value |
| --- | --- |
| ROS distro | Noetic |
| ROS master | `http://localhost:11311` |
| Workspace path | `/home/robot/catkin_ws/src` |
| Cartographer ROS path | `/home/robot/cartographer/src/cartographer_ros/...` |
| System ROS path | `/opt/ros/noetic/share` |

Important installed ROS Debian package families observed:

- Core: `ros-noetic-ros-base`, `ros-noetic-ros-core`, `ros-noetic-ros-comm`, `ros-noetic-desktop`, `ros-noetic-desktop-full`
- Navigation: `move_base`, `costmap_2d`, `nav_core`, `nav_msgs`, `map_msgs`, `global_planner`, `dwa_local_planner`, `teb_local_planner`, `navfn`, `amcl`
- Perception and image: `cv_bridge`, `image_transport`, `image_pipeline`, `image_proc`, `depth_image_proc`, `camera_info_manager`, `pcl_ros`, `pcl_conversions`
- Sensors: `apriltag_ros`, `realsense2_camera`, `laser_geometry`, `laser_filters`, `laser_pipeline`
- Control: `controller_manager`, `diff_drive_controller`, `control_msgs`, `hardware_interface`
- Visualization/dev: `rviz`, `rqt`, Gazebo-related ROS packages

## Workspace Inventory

`/home/robot/catkin_ws/src` includes:

- Chassis/control drivers: `dt_control`, `ros_dt_msg`, `ros_four1_msg`, `ros_pt_msg`, `four_wheel`, `ros_agv3_msg`
- Robot application bridges: `ros_robot_control_mqtt`, `ros_mqtt_modbus`, `ros_mqtt_transition`
- Navigation: `zkwl_robot_start`, `scan_icp_matcher`, `snap_map_icp_zxp`, `move_base_virtual_wall_server`, `ros_half_planner`, `ros_magnetic_nav_service`, local copy of navigation packages
- Sensors: `fdilink_ahrs`, `laser_udp`, `vanjee_lidar_sdk`, `rslidar_sdk`, `astra_camera`, `pointcloud_to_laserscan`, `ira_laser_tools`, `nvilidar_ros`, `bluesea2`, `hins_de_driver`, `wj_716_lidar`, `wj_716N_lidar`
- Actuators/status: `ros_hosting`, `zk_lifting_ros`, `ros_bms_msg`, `cmd_vel_voice`
- Fiducial/camera localization: `usb_cam`, `apriltag_detection`, `apriltag_tracker`, `ar_pose_tracker`

`/home/robot/cartographer/src` includes:

- `cartographer`
- `cartographer_ros`
- `cartographer_rviz`
- `cartographer_ros_msgs`
- `ceres-solver-1.13.0`

## Startup and Operating Modes

Default/manual startup:

- `/home/robot/mysh/robot_start.sh`
- Starts:
  - `roscore`
  - `ros_robot_control_mqtt`
  - `ros_mqtt_modbus`

Operator note:

- The navigation framework is described as boot-autostarted.
- Entering navigation or mapping mode may close other nodes.

Mapping mode:

- Launch: `zkwl_robot_start/launch/carto_slam.launch`
- Major includes:
  - robot custom TF/config
  - IMU
  - base control
  - VanJee 3D lidar
  - two UDP 2D lidars
  - pointcloud-to-laserscan
  - laser scan merger
  - odometry publisher
  - Cartographer mapping
  - BMS

Navigation/localization mode:

- Launch: `zkwl_robot_start/launch/move_base.launch`
- Major includes:
  - same base sensor/control stack
  - `map_server`
  - Cartographer localization from saved state
  - `move_base`
  - virtual wall server
  - scan ICP matcher
  - BMS
  - half planner
  - MQTT transition
  - voice velocity command
  - brush/door actuator nodes

## Sensor and Driver Configuration

IMU:

- Package: `fdilink_ahrs`
- Launch: `ahrs_data.launch`
- Serial alias: `/dev/imu_usb`
- Baud: `921600`
- IMU topic: `/sensor_imu`
- IMU frame: `gyro_link`
- Magnetic pose topic: `/mag_pose_2d`

2D lidar:

- Package: `laser_udp`
- Launch: `laser_udp_with_1_lidar.launch`
- Two nodes: `laser1`, `laser2`
- Topics: `/scan_front`, `/scan_back`
- Frames: `laser_front`, `laser_back`
- Angle range: approximately `[-1.919862177, 1.919862177]`
- Range: `0.01` to `60.0`
- Device network addresses are private and redacted.

3D lidar:

- Package: `vanjee_lidar_sdk`
- Launch: `start.launch`
- Node: `vanjee_lidar_sdk_node`
- Point cloud topic documented as `/points_raw`
- Device/host network addresses are private and redacted.

Depth camera:

- Package: `astra_camera`
- Documented launch: `astra_pro_plus.launch`
- RGB topic: `/camera/color/image_raw`
- Depth topic: `/camera/depth/image_raw`

Scan fusion and conversion:

- `pointcloud_to_laserscan` consumes `/scan_matched_points2` and emits a laser scan in target frame `laser`.
- `ira_laser_tools/laserscan_multi_merger.launch` fuses `/scan_front` and `/scan_back` into `/scan_ira`, with cloud output `/merged_cloud` and destination frame `laser_ira`.

## Navigation Configuration

Cartographer mapping/localization:

- Uses `my_robot_3d.lua` for mapping.
- Uses saved-state localization launch with `my_backpack_3d_localization.lua` and `map.pbstream`.
- Frames:
  - `map_frame = map`
  - `tracking_frame = gyro_link`
  - `published_frame = base_footprint`
  - `odom_frame = odom`
- Inputs:
  - point cloud: `/points_raw`
  - IMU remap: `/robot_imu`
  - odometry: `/odom`
- Uses odometry and IMU data.
- 2D trajectory builder is enabled for range data from one point cloud stream.

`move_base`:

- Base local planner: `teb_local_planner/TebLocalPlannerROS`
- Global planner parameters loaded from `global_planner_params.yaml`.
- TEB, costmap, global costmap, local costmap, and move_base parameters loaded from `zkwl_robot_start/param`.

Costmaps:

- Global costmap:
  - frame: `map`
  - robot base: `base_footprint`
  - static map enabled
  - plugins: static layer, voxel obstacle layer, inflation layer
- Local costmap:
  - frame: `odom`
  - robot base: `base_footprint`
  - rolling window enabled
  - size: 6 m x 6 m
  - resolution: 0.05 m
  - plugins: obstacle layer, inflation layer
- Observation topics:
  - `/scan`
  - `/scan_ira`
  - `/virtual_wall_cloud`

TEB local planner selected parameters:

- `odom_topic = odom`
- `max_vel_x = 0.5`
- `max_vel_x_backwards = 0.11`
- `max_vel_theta = 0.5`
- `acc_lim_x = 0.11`
- `acc_lim_theta = 0.11`
- `xy_goal_tolerance = 0.2`
- `yaw_goal_tolerance = 0.1`
- polygon footprint model
- homotopy planning enabled, limited to one class

Global planner selected parameters:

- `allow_unknown = false`
- `default_tolerance = 0.2`
- `use_dijkstra = true`
- `use_quadratic = true`
- `publish_potential = true`

## Runtime Status

Runtime ROS inspection attempted before startup/sandbox escalation:

- `rostopic list -v`
- `rosnode list`
- `rosparam list`

Initial result:

- All failed with `Unable to communicate with master`.

After the ROS system was started and queried from the host namespace, the live graph was available.

Active launch/process chain:

- `roscore` and `rosmaster` on port 11311.
- Startup script-launched `ros_robot_control_mqtt` and `ros_mqtt_modbus`.
- `roslaunch /home/robot/catkin_ws/src/ros_nav/zkwl_robot_start/launch/move_base.launch`.
- Active navigation mode includes Cartographer localization, static map server, `move_base`, lidar conversion/fusion, virtual walls, scan ICP helpers, BMS, MQTT bridge, chassis driver, and cleaning-actuator nodes.

Live ROS nodes observed:

- `/SnapMapICPZXP`
- `/ahrs_driver`
- `/base_to_gyro`, `/base_to_laser`, `/base_to_laser_ira`, `/base_to_link`, `/base_to_velodyne`
- `/cartographer_node`
- `/cmd_vel_voice`
- `/dt_control_node`
- `/hosting_node`
- `/ira_static_broadcaster1`, `/ira_static_broadcaster2`
- `/laser1`, `/laser2`
- `/laserscan_multi_merger`
- `/map_server_for_test`
- `/move_base`
- `/pattern_matcher`
- `/pointcloud_to_laserscan`
- `/publish_odom`
- `/ros_bms_talker`
- `/ros_end_control`
- `/ros_half_planner`
- `/ros_mqtt_transition`
- `/ros_robot_control_node`
- `/rosout`
- `/vanjee_lidar_sdk_node`
- `/virtual_wall_server`
- `/zk_lifting_ros_node`

Live topic-rate sample:

| Topic | Message type | Approx. rate |
| --- | --- | ---: |
| `/robot_imu` | `sensor_msgs/Imu` | 100 Hz |
| `/odom` | `nav_msgs/Odometry` | 50 Hz |
| `/scan_front` | `sensor_msgs/LaserScan` | 20 Hz |
| `/scan_back` | `sensor_msgs/LaserScan` | 20 Hz |
| `/points_raw` | `sensor_msgs/PointCloud2` | 10 Hz |
| `/scan` | `sensor_msgs/LaserScan` | 10 Hz |

No message payloads were retained.

Key live services:

- Cartographer: `/submap_query`, `/trajectory_query`, `/start_trajectory`, `/finish_trajectory`, `/write_state`, `/read_metrics`
- Navigation: `/move_base/make_plan`, `/move_base/clear_costmaps`, `/move_base/GlobalPlanner/make_plan`
- Virtual walls: `/virtual_wall_server/create_wall`, `/virtual_wall_server/delete_wall`, `/virtual_wall_server/delete_all`
- Pattern/ICP: `/pattern_file_load`
- Dynamic reconfigure and logger services for lidar, scan merger, planners, costmaps, and major nodes

## Runtime Logic Summary

`ros_robot_control_node`:

- Main application controller and MQTT bridge.
- Starts MQTT polling plus callback-processing threads, then runs ROS callbacks through an 8-thread async spinner.
- Subscribes to `robot_control` over MQTT and translates commands into ROS navigation, charge, stop, fault-clear, map, wall, track, location, and actuator actions.
- Publishes `/move_base_simple/goal`, `/move_base/cancel`, `/cmd_vel`, `/dt/charge_ctrl`, `/dt/collision_clean`, `/reset_pose`, `/initialpose1`, `/robot_imu`, `/ros_hosting_issue`, and motor speed topics.
- Subscribes to `/move_base/result`, `/move_base/status`, `/move_base/GlobalPlanner/plan`, `/dt/state_info`, `/dt/charge_info`, `/scan`, `/map`, `/sensor_imu`, `/icp_status`, `/icp_fitness_score`, `/constraint_list`, `/kuma_bms_info`, and actuator feedback.
- Sends status and feedback back to MQTT, including base status, navigation/task feedback, selected path/scan metadata, and map-related control responses.

`ros_mqtt_transition`:

- Independent transition bridge between ROS messages and MQTT JSON.
- Converts `/point_control`, `/charge_control`, and `/error_reset` into MQTT `robot_control` messages.
- Converts MQTT `base_status` and `task_feedback` into ROS `/base_status_info` and `/task_feedback_info`.

`publish_odom`:

- Integrates chassis linear velocity from active chassis status and yaw rate from `/robot_imu`.
- Publishes `/odom` at the active chassis update rate, observed around 50 Hz.

`dt_control_node`:

- DT chassis serial driver.
- Consumes `/cmd_vel` through launch remap to `/dt/velocity_ctrl`.
- Publishes `/dt/state_info`, `/dt/odom_info`, charge/status/current/version/parameter topics, and consumes stop/charge/fault-clean controls.

Hardware enumeration:

- `lspci` detected Intel platform devices, Intel Ethernet, Intel integrated graphics, NVIDIA PCI graphics/audio, NVMe storage, and Renesas USB controller.
- `lsusb` could not initialize libusb from the sandboxed environment, so attached USB sensor details could not be verified live.

## Privacy and Safety Handling

Excluded from repository output:

- Passwords and remote-access secrets found in local notes.
- Wi-Fi SSIDs/passwords.
- Client usernames/passwords.
- Full private IP addresses from launch files and notes.
- Raw sensor streams: image, depth, point cloud, LaserScan samples, IMU samples, odometry samples.
- ROS logs, bag files, point cloud files, maps as raw artifacts, shell history, SSH/GPG material, browser/profile data, package caches, binaries, and archives.

Included:

- Topic names, package names, launch relationships, frame names, planner/costmap parameter summaries, and non-sensitive system capacity data.
