# ROS Topic Inventory

Generated: 2026-07-01 16:30 CST
Runtime ROS refresh: 2026-07-01, after navigation stack startup

This inventory combines the live ROS graph after startup with launch-file and local operator-note context. It does not include message samples, raw sensor payloads, log excerpts, credentials, or full private network addresses.

## Runtime Query Result

Commands attempted from the initial sandbox namespace:

- `rostopic list -v`
- `rosnode list`
- `rosparam list`

Initial result:

- `ERROR: Unable to communicate with master!`

After querying from the host namespace, live node/topic/service metadata was available. Publisher/subscriber counts, message types, node liveness, and short rate samples below reflect that host-namespace query.

## Live Nodes

| Node | Role |
| --- | --- |
| `/ros_robot_control_node` | Main application controller and MQTT command/status bridge |
| `/ros_mqtt_transition` | ROS/MQTT transition bridge for point, charge, error reset, base status, and task feedback |
| `/dt_control_node` | DT chassis serial driver |
| `/publish_odom` | Chassis velocity plus IMU yaw integration into `/odom` |
| `/cartographer_node` | Cartographer localization from saved map state |
| `/move_base` | Navigation action server, global planner, TEB local planner, costmaps |
| `/map_server_for_test` | Static map server |
| `/laser1`, `/laser2` | Front and rear 2D lidar drivers |
| `/vanjee_lidar_sdk_node` | 3D lidar driver |
| `/pointcloud_to_laserscan` | Converts Cartographer matched point cloud to LaserScan |
| `/laserscan_multi_merger` | Merges front/rear LaserScan into `/scan_ira` |
| `/virtual_wall_server` | Publishes virtual-wall point cloud obstacles |
| `/SnapMapICPZXP`, `/pattern_matcher`, `/ros_end_control` | Scan/map ICP and end-control helpers |
| `/ros_half_planner` | Half-planner / traffic path helper |
| `/ros_bms_talker` | BMS status publisher |
| `/hosting_node`, `/zk_lifting_ros_node` | Cleaning/door/brush actuator control |
| `/ahrs_driver` | IMU/GNSS/magnetic heading driver |
| static TF nodes | Base, gyro, lidar, velodyne, and fused-lidar frame transforms |

## Live Topic Rates

| Topic | Message type | Approx. rate |
| --- | --- | ---: |
| `/robot_imu` | `sensor_msgs/Imu` | 100 Hz |
| `/odom` | `nav_msgs/Odometry` | 50 Hz |
| `/scan_front` | `sensor_msgs/LaserScan` | 20 Hz |
| `/scan_back` | `sensor_msgs/LaserScan` | 20 Hz |
| `/points_raw` | `sensor_msgs/PointCloud2` | 10 Hz |
| `/scan` | `sensor_msgs/LaserScan` | 10 Hz |

## Core Frames

| Frame | Role |
| --- | --- |
| `map` | Global map frame for Cartographer and global costmap |
| `odom` | Odometry frame and local costmap global frame |
| `base_footprint` | Published robot base frame |
| `gyro_link` | IMU tracking frame |
| `laser_front` | Front 2D lidar frame |
| `laser_back` | Rear 2D lidar frame |
| `laser_ira` | Fused 2D scan destination frame |
| `laser` | Pointcloud-to-laserscan target frame |

## Sensor Topics

| Topic | Direction | Source / Consumer | Notes |
| --- | --- | --- | --- |
| `/sensor_imu` | publish | `fdilink_ahrs` | IMU topic configured in `ahrs_data.launch` |
| `/mag_pose_2d` | publish | `fdilink_ahrs` | Magnetic heading pose topic |
| `/scan_front` | publish | `laser_udp` node `laser1` | Front 2D lidar scan |
| `/scan_back` | publish | `laser_udp` node `laser2` | Rear 2D lidar scan |
| `/points_raw` | publish | `vanjee_lidar_sdk` | 3D lidar point cloud; consumed by Cartographer via `points2` remap |
| `/camera/color/image_raw` | publish | `astra_camera` | RGB image topic from local notes; raw image data not collected |
| `/camera/depth/image_raw` | publish | `astra_camera` | Depth image topic from local notes; raw image data not collected |
| `/scan_matched_points2` | subscribe | `pointcloud_to_laserscan` | Point cloud input to synthetic 2D scan conversion |
| `/scan` | publish/consume | pointcloud-to-laserscan / costmap / Cartographer remap | Generic scan topic used by costmap and Cartographer launch remap |
| `/scan_ira` | publish | `ira_laser_tools` | Fused scan from `/scan_front` and `/scan_back` |
| `/merged_cloud` | publish | `ira_laser_tools` | Fused cloud output from multi-scan merger |

## Localization, Mapping, and Navigation Topics

| Topic | Direction | Source / Consumer | Notes |
| --- | --- | --- | --- |
| `/odom` | publish/consume | base odometry / Cartographer / TEB | Cartographer remaps `odom -> /odom`; TEB uses `odom_topic = odom` |
| `/robot_imu` | consume | Cartographer | Cartographer remaps `imu -> /robot_imu`; local IMU driver publishes `/sensor_imu`, so a bridge/remap may exist in custom launch |
| `/map` | publish/consume | `map_server`, Cartographer occupancy grid, costmap static layer | Map topic used by global costmap static layer |
| `/virtual_wall_cloud` | publish/consume | `move_base_virtual_wall_server`, costmap | PointCloud2 virtual wall obstacle source |
| `/move_base/*` | action/topics | `move_base` | Standard ROS navigation action/control namespace inferred from `move_base` node |
| `/tf` | publish/consume | TF publishers, Cartographer, navigation stack | Transform tree |
| `/tf_static` | publish/consume | static TF publishers | Static transforms, including scan-merger transforms |

## Chassis / Base Topics

From local operator notes for the DT chassis stack:

| Topic | Direction | Purpose |
| --- | --- | --- |
| `/dt/buff_info` | publish | Raw chassis/buffer status metadata; samples not collected |
| `/dt/charge_info` | publish | Charging status |
| `/dt/current_info` | publish | Motor current |
| `/dt/date_info` | publish | Production/date metadata |
| `/dt/drive_error_info` | publish | Drive error status |
| `/dt/hardware_version_info` | publish | Hardware version |
| `/dt/parameter_info` | publish | Chassis parameters |
| `/dt/remote_ctrl_info` | publish | Remote-control status |
| `/dt/software_version_info` | publish | Software version |
| `/dt/state_info` | publish | Chassis state |
| `/dt/odom_info` | publish | Chassis odometry |
| `/dt/velocity_ctrl` | subscribe | Linear/angular velocity command |
| `/dt/stop_ctrl` | subscribe | Emergency stop control |
| `/dt/collision_clean` | subscribe | Clear collision state |
| `/dt/fault_clean` | subscribe | Clear fault state |
| `/dt/charge_ctrl` | subscribe | Charging control |
| `/dt/odom_clean` | subscribe | Clear odometry |

## Actuator and Cleaning-Mechanism Topics

| Topic | Direction | Source / Consumer | Notes |
| --- | --- | --- | --- |
| `/ros_hosting_issue` | subscribe | `ros_hosting` | Brush lift control, e.g. up/down command |
| `/motor/speed_percent` | subscribe | `zk_lifting_ros_node` | Door/lift motor speed percentage |
| `/motor/speed_percent_02` | subscribe | `zk_lifting_ros_node` | Brush motor speed percentage |
| `/motor/speed_percent_03` | subscribe | `zk_lifting_ros_node` | Brush motor speed percentage |
| `/motor/limit_status` | publish | `zk_lifting_ros_node` | Door/lift limit and run state |

## Battery and Auxiliary Topics

| Topic / Namespace | Direction | Source / Consumer | Notes |
| --- | --- | --- | --- |
| `ros_bms_msg` topics | publish/consume | `ros_bms_msg.launch` | Exact runtime names require live ROS master or package-specific message inspection |
| `cmd_vel_voice` topics | publish/consume | `cmd_vel_voice.launch` | Voice velocity command package included by navigation launch |
| `ros_mqtt_transition` topics | publish/consume | `ros_mqtt_transition.launch` | MQTT bridge topics require live ROS graph to enumerate fully |
| `ros_mqtt_modbus` topics | publish/consume | `ros_mqtt_modbus` startup | Modbus bridge node starts from robot startup script |

## Nodes Inferred From Launch Files

| Node | Package | Launch / Mode | Role |
| --- | --- | --- | --- |
| `roscore` | ROS core | startup script | ROS master |
| `ros_robot_control_mqtt` | `ros_robot_control_mqtt` | startup script | Robot application/control bridge |
| `ros_mqtt_modbus` | `ros_mqtt_modbus` | startup script | MQTT/Modbus bridge |
| `ahrs_driver` | `fdilink_ahrs` | mapping/navigation | IMU driver |
| `laser1` | `laser_udp` | mapping/navigation | Front 2D lidar |
| `laser2` | `laser_udp` | mapping/navigation | Rear 2D lidar |
| `vanjee_lidar_sdk_node` | `vanjee_lidar_sdk` | mapping/navigation | 3D lidar driver |
| `pointcloud_to_laserscan` | `pointcloud_to_laserscan` | mapping/navigation | Converts point cloud to LaserScan |
| `laserscan_multi_merger` | `ira_laser_tools` | mapping/navigation | Merges front/rear lidar scans |
| `ira_static_broadcaster1` | `tf` | mapping/navigation | Static transform for scan fusion |
| `ira_static_broadcaster2` | `tf` | mapping/navigation | Static transform for scan fusion |
| `publish_odom` | `zkwl_robot_start` | mapping/navigation | Robot odometry publishing |
| `cartographer_node` | `cartographer_ros` | mapping/navigation | SLAM/localization |
| `cartographer_occupancy_grid_node` | `cartographer_ros` | mapping | Occupancy grid generation |
| `map_server_for_test` | `map_server` | navigation | Static map server |
| `move_base` | `move_base` | navigation | Navigation action server and planners |
| `virtual_wall_server` | `move_base_virtual_wall_server` | navigation | Virtual wall obstacle source |
| `SnapMapICPZXP` | `snap_map_icp_zxp` | navigation | Map/scan ICP alignment helper |
| `scan_icp_matcher` launch nodes | `scan_icp_matcher` | navigation | Scan ICP matching |
| `zk_lifting_ros_node` | `zk_lifting_ros` | navigation | Door/brush motor control |

## Expected Topic Flow

1. 2D lidar drivers publish `/scan_front` and `/scan_back`.
2. `ira_laser_tools` merges those scans into `/scan_ira` and `/merged_cloud`.
3. 3D lidar publishes `/points_raw`.
4. Cartographer consumes `/points_raw`, odometry, and IMU data to publish localization/map-related outputs.
5. `map_server` and/or Cartographer provide `/map`.
6. `move_base` consumes map, TF, odometry, scan/costmap observations, and goals to produce navigation commands.
7. Chassis/control nodes consume velocity/control topics and publish state/odometry topics.
8. Actuator nodes expose brush, door, and cleaning-mechanism command/status topics.

## Verification Gaps

- Live message types and rates were not available because ROS master was offline or unreachable.
- USB-attached device inventory was not available because `lsusb` failed inside the sandbox.
- Exact `ros_bms_msg`, `cmd_vel_voice`, MQTT bridge, and custom control topic names should be verified from a live ROS graph or package-specific message definitions before relying on them for automated experiments.
