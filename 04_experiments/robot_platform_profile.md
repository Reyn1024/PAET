# Robot Platform Profile

Generated: 2026-07-01 16:30 CST
Runtime ROS refresh: 2026-07-01, after navigation stack startup

This profile summarizes the local Ubuntu robot platform for PAET experiments. It intentionally excludes raw sensor captures, logs, credentials, Wi-Fi information, remote-access passwords, MAC addresses, and full network addresses. Private IP addresses found in local startup notes and launch files are represented only as redacted private-network endpoints.

## Collection Scope

- Host OS, kernel, CPU thread count, memory, and storage capacity.
- ROS distribution, workspace layout, locally available robot packages, and navigation/sensor launch structure.
- Topic inventory from live ROS graph after the navigation stack was started, supplemented by launch files and operator notes.
- Navigation stack configuration summary from `zkwl_robot_start`, Cartographer, `move_base`, TEB, costmap, and related launch files.

## Platform Summary

| Item | Value |
| --- | --- |
| OS | Ubuntu 20.04.6 LTS (focal) |
| Kernel | Linux 5.15.0-139-generic, x86_64 |
| CPU threads | 20 |
| Memory | 15 GiB RAM, 2 GiB swap |
| Root filesystem | 938 GiB NVMe-backed filesystem, about 45 GiB used at collection time |
| ROS | ROS 1 Noetic |
| ROS master URI | `http://localhost:11311` |
| ROS package path | `catkin_ws/src`, Cartographer ROS packages, `/opt/ros/noetic/share` |
| GPU/accelerator | Intel integrated graphics and NVIDIA PCI device detected |
| USB inventory | Not available from sandboxed collection: `lsusb` failed with libusb initialization error |

Host-identifying values are omitted or generalized in this report.

## ROS Workspaces

Primary workspace:

- `/home/robot/catkin_ws`
- Source tree contains custom robot control, chassis drivers, sensor drivers, navigation packages, MQTT/Modbus bridge packages, and application-specific robot startup packages.

Cartographer workspace:

- `/home/robot/cartographer`
- Contains Cartographer, `cartographer_ros`, `cartographer_rviz`, `cartographer_ros_msgs`, and Ceres Solver sources/build artifacts.

## Major Local ROS Packages

Robot control and integration:

- `ros_robot_control_mqtt`
- `ros_mqtt_modbus`
- `ros_mqtt_transition`

Chassis/base drivers:

- `dt_control`, `dt_control_msgs`
- `ros_dt_msg`
- `ros_four1_msg`
- `ros_pt_msg`
- `four_wheel`, `four_wheel_msgs`
- `ros_agv3_msg`

Sensors and actuators:

- `fdilink_ahrs`
- `laser_udp`
- `vanjee_lidar_sdk`
- `rslidar_sdk`
- `astra_camera`
- `pointcloud_to_laserscan`
- `ira_laser_tools`
- `nvilidar_ros`
- `bluesea2`
- `hins_de_driver`
- `wj_716_lidar`
- `wj_716N_lidar`
- `ros_hosting`
- `zk_lifting_ros`
- `cmd_vel_voice`
- `ros_bms_msg`

Navigation and localization:

- `zkwl_robot_start`
- `move_base`
- `costmap_2d`
- `global_planner`
- `teb_local_planner`
- `dwa_local_planner`
- `map_server`
- `amcl`
- `navfn`
- `scan_icp_matcher`
- `snap_map_icp_zxp`
- `move_base_virtual_wall_server`
- `ros_half_planner`
- `ros_magnetic_nav_service`
- `cartographer_ros`

Perception/local fiducial packages:

- `usb_cam`
- `apriltag_detection`
- `apriltag_tracker`
- `ar_pose_tracker`
- `ar_track_alvar_msgs`

## Physical Sensor/Actuator Profile

The following is inferred from launch files and local operator notes. Network endpoints and credentials were found locally but are redacted.

| Subsystem | ROS package / launch | Interfaces / topics |
| --- | --- | --- |
| IMU | `fdilink_ahrs/launch/ahrs_data.launch` | Publishes `/sensor_imu`, frame `gyro_link`, serial device alias `/dev/imu_usb`, baud `921600` |
| 2D lidar pair | `laser_udp/launch/laser_udp_with_1_lidar.launch` | Publishes `/scan_front` and `/scan_back`, frames `laser_front` and `laser_back`; private device IPs redacted |
| 3D lidar | `vanjee_lidar_sdk/launch/start.launch` | Publishes point cloud stream documented as `/points_raw`; private device/host IPs redacted |
| Depth camera | `astra_camera` launch variants, documented default `astra_pro_plus.launch` | `/camera/color/image_raw`, `/camera/depth/image_raw` |
| Chassis/base | `dt_control/launch/dt_control.launch` plus `zkwl_robot_start` odometry node | Velocity, stop, charge, odometry, state, and fault-control topics under `/dt/*` |
| Brush lifting | `ros_hosting/launch/zkwl_hosting.launch` | Control topic `/ros_hosting_issue` |
| Door/brush motor control | `zk_lifting_ros_node` | `/motor/speed_percent`, `/motor/speed_percent_02`, `/motor/speed_percent_03`, `/motor/limit_status` |
| BMS | `ros_bms_msg/launch/ros_bms_msg.launch` | Battery-management topics from package launch; exact runtime topics require live ROS master |

## Live Runtime Profile

After startup, the active mode was navigation/localization via `zkwl_robot_start/launch/move_base.launch`.

Running ROS nodes observed:

- `/ros_robot_control_node`
- `/ros_mqtt_transition`
- `/dt_control_node`
- `/ahrs_driver`
- `/laser1`, `/laser2`
- `/vanjee_lidar_sdk_node`
- `/cartographer_node`
- `/pointcloud_to_laserscan`
- `/laserscan_multi_merger`
- `/map_server_for_test`
- `/move_base`
- `/virtual_wall_server`
- `/SnapMapICPZXP`
- `/pattern_matcher`
- `/ros_end_control`
- `/ros_half_planner`
- `/ros_bms_talker`
- `/hosting_node`
- `/zk_lifting_ros_node`
- static TF publishers for base, gyro, lidar, velodyne, and fused lidar frames

Observed topic rates over a short metadata-only sample:

| Topic | Approx. rate |
| --- | ---: |
| `/robot_imu` | 100 Hz |
| `/odom` | 50 Hz |
| `/scan_front` | 20 Hz |
| `/scan_back` | 20 Hz |
| `/points_raw` | 10 Hz |
| `/scan` | 10 Hz |

The sample used `rostopic hz` only to compute rates; message payloads were not stored.

## Navigation Stack Profile

Startup and high-level launch:

- Manual/default startup entry: `/home/robot/mysh/robot_start.sh`
- The script starts `roscore`, `ros_robot_control_mqtt`, and `ros_mqtt_modbus` in terminal tabs.
- Operator notes indicate the navigation framework is configured for boot-time autostart, and manual startup uses `sh /home/robot/mysh/robot_start.sh`.

SLAM launch:

- `zkwl_robot_start/launch/carto_slam.launch`
- Includes robot TF/custom launch, IMU, `dt_control`, VanJee lidar, 2D lidar, pointcloud-to-laserscan, laser scan merger, odometry publishing, Cartographer mapping, BMS, and custom robot parameters.

Navigation launch:

- `zkwl_robot_start/launch/move_base.launch`
- Includes the same base sensor/control stack, map server, Cartographer 3D localization from saved state, `move_base`, virtual wall server, scan ICP matcher, BMS, half planner, MQTT transition, voice velocity command, brush/door actuator nodes, and custom parameters.

Cartographer:

- Mapping launch: `cartographer_ros/launch/my_getmap_3d.launch`
- Localization launch: `cartographer_ros/launch/my_robot_3d_localization.launch`
- 3D input topic remaps include `points2 -> /points_raw`, `imu -> /robot_imu`, and `odom -> /odom`.
- Configuration uses a 2D trajectory builder over point cloud input:
  - `map_frame = map`
  - `tracking_frame = gyro_link`
  - `published_frame = base_footprint`
  - `odom_frame = odom`
  - `use_odometry = true`
  - `num_point_clouds = 1`
  - `TRAJECTORY_BUILDER_2D.min_range = 0.01`
  - `TRAJECTORY_BUILDER_2D.max_range = 30.0`
- `TRAJECTORY_BUILDER_2D.use_imu_data = true`
- `MAP_BUILDER.num_background_threads = 8`

Live Cartographer node:

- Publishes `/tf`, `/submap_list`, `/trajectory_node_list`, `/constraint_list`, `/landmark_poses_list`, and `/scan_matched_points2`.
- Subscribes to `/points_raw`, `/robot_imu`, `/odom`, `/initialpose1`, `/reset_pose`, `/tf`, and `/tf_static`.
- Exposes standard Cartographer services such as `/submap_query`, `/trajectory_query`, `/start_trajectory`, `/finish_trajectory`, `/write_state`, and `/read_metrics`.

`move_base`:

- Base local planner: `teb_local_planner/TebLocalPlannerROS`
- Global planner parameters are loaded from `global_planner_params.yaml`.
- Costmap parameters are loaded into global and local namespaces from `costmap_common_params.yaml`, `global_costmap_params.yaml`, and `local_costmap_params.yaml`.

Live `move_base` node:

- Publishes `/cmd_vel`, global and local plans, TEB visualization/feedback, costmap grids/updates, action result/status/feedback, current goal, recovery status, and dynamic-reconfigure metadata.
- Subscribes to `/map`, `/odom`, `/scan`, `/scan_ira`, `/virtual_wall_cloud`, `/move_base_simple/goal`, `/move_base/goal`, `/move_base/cancel`, `/tf`, and `/tf_static`.
- Provides `/move_base/make_plan`, `/move_base/clear_costmaps`, dynamic-reconfigure services, and global planner make-plan service.

## Control and Bridge Logic

`ros_robot_control_node` is the main robot application bridge:

- Starts an MQTT polling thread and a callback-processing thread, then uses an 8-thread ROS async spinner.
- Connects to the local MQTT broker at a loopback/all-interfaces broker address on port 1883 and subscribes to `robot_control`.
- Publishes navigation goals, cancels, charge controls, velocity commands, initial pose, reset pose, IMU bridge output, fault/stop controls, hosting commands, and motor speed commands.
- Subscribes to navigation results/status, global plan, base/chassis state, map, scan, ICP status, BMS info, motor limit status, and Cartographer constraints.
- Bridges `/sensor_imu` into `/robot_imu`, which is consumed by Cartographer and odometry logic.
- Periodically enqueues status, global path, scan-derived metadata, task feedback, and other JSON/MQTT messages. Raw scan/map payloads were not copied into this report.

`ros_mqtt_transition` is a narrower MQTT transition bridge:

- Subscribes to ROS topics `/point_control`, `/error_reset`, and `/charge_control`.
- Publishes MQTT `robot_control` JSON commands for interest-point navigation, error reset, and charge-point control.
- Subscribes to MQTT `base_status` and `task_feedback`, parses JSON, and republishes sanitized ROS messages on `/base_status_info` and `/task_feedback_info`.

`publish_odom` (`zkwl_robot_start/zkwl_robot_node`) fuses chassis velocity and IMU yaw rate into `/odom`:

- Subscribes to multiple possible chassis-state topics, with the active DT path using `/dt/state_info`.
- Subscribes to `/robot_imu`.
- Integrates linear velocity and IMU angular velocity over time, publishes `nav_msgs/Odometry` on `/odom`, and sets `child_frame_id` to `base_footprint`.

`dt_control_node` is the DT chassis serial driver:

- Subscribes to `/dt/velocity_ctrl`, `/dt/stop_ctrl`, `/dt/collision_clean`, `/dt/fault_clean`, `/dt/charge_ctrl`, and `/dt/odom_clean`.
- In the live launch, `/dt/velocity_ctrl` is remapped from `/cmd_vel`.
- Publishes DT status, charge, current, version, parameter, remote-control, state, and odometry topics under `/dt/*`.
- Runs serial read/write and package-loop timers at millisecond-scale intervals.

Costmap:

- Robot footprint: rectangular polygon, approximately front-biased footprint from local config.
- Global frame: `map`
- Local frame: `odom`
- Robot base frame: `base_footprint`
- Local rolling window: enabled, 6 m by 6 m, 0.05 m resolution.
- Observation sources: `/scan`, `/scan_ira`, and `/virtual_wall_cloud`.
- Inflation radius: `0.4`
- Obstacle range: `2.5`
- Raytrace range: `3`

TEB local planner:

- `max_vel_x = 0.5`
- `max_vel_x_backwards = 0.11`
- `max_vel_theta = 0.5`
- `acc_lim_x = 0.11`
- `acc_lim_theta = 0.11`
- `xy_goal_tolerance = 0.2`
- `yaw_goal_tolerance = 0.1`
- Polygon footprint model configured.
- Homotopy class planning enabled with one active class.

Global planner:

- `allow_unknown = false`
- `use_dijkstra = true`
- `use_quadratic = true`
- `default_tolerance = 0.2`
- `publish_potential = true`

## Data Handling Notes

- No bag files, raw images, point clouds, maps, logs, shell history, SSH material, browser data, credential files, or secret stores were copied into this repository.
- Local notes contained passwords, Wi-Fi names, remote-access credentials, and private IP addresses. They were intentionally excluded.
- Private IPs embedded in launch/config files were not reproduced in full.
- Runtime ROS topic inspection initially failed inside the sandbox namespace, but succeeded from the host namespace after the ROS stack was started.
