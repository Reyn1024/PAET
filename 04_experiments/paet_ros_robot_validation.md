# PAET ROS Robot Validation

Date: 2026-07-14

Repository revision validated: `6477bf9 Add PAET ROS V1 package scaffold`

## Scope

This validation checked the ROS 1 Noetic `paet_ros` package from `ros/paet_ros` on the local robot workspace.

The package was copied to:

```text
/home/robot/catkin_ws/src/paet_ros
```

The scripts were made executable:

```bash
chmod +x /home/robot/catkin_ws/src/paet_ros/scripts/*.py
chmod +x /home/robot/PAET/ros/paet_ros/scripts/*.py
```

## Build Result

Command:

```bash
cd /home/robot/catkin_ws
catkin_make
```

Result: passed.

Observed PAET build outputs:

- `paet_ros: 2 messages, 0 services`
- devel wrappers installed for:
  - `paet_geometry_tokenizer.py`
  - `paet_event_logger.py`
  - `paet_eval_helper.py`
- message generation target `paet_ros_generate_messages` completed.

Existing workspace warnings were observed for unrelated packages, including `wj_716N_lidar` package naming and VTK imported target warnings. These did not stop the build.

## Runtime Startup

The normal robot stack was started through the robot control node, not by manually launching `move_base.launch`:

```bash
source ~/.bashrc
cd /home/robot/catkin_ws
source /home/robot/catkin_ws/devel/setup.bash
rosrun ros_robot_control_mqtt ros_robot_control_mqtt
```

Runtime result:

- `ros_robot_control_mqtt` started `zkwl_robot_start/launch/move_base.launch`.
- `/move_base` was present.
- `/ros_robot_control_node` was present.
- MQTT connection opened successfully in the control-node log.

The Modbus/MQTT bridge was started separately:

```bash
source ~/.bashrc
cd /home/robot/catkin_ws
source /home/robot/catkin_ws/devel/setup.bash
rosrun ros_mqtt_modbus ros_mqtt_modbus
```

Runtime result:

- `initModbus is sucess`
- MQTT connection opened and subscribed successfully.

PAET was then started:

```bash
source ~/.bashrc
cd /home/robot/catkin_ws
source /home/robot/catkin_ws/devel/setup.bash
roslaunch paet_ros paet_v1.launch
```

Runtime result:

- `/paet_geometry_tokenizer` started.
- `/paet_event_logger` started.
- Tokenizer selected `scan_topic=/scan_ira`.
- Event logger wrote to `~/.ros/paet_logs`.

## Input Topic Checks

Key inputs were available:

| Topic | Result |
| --- | --- |
| `/scan_ira` | approximately 20 Hz |
| `/map` | header received, frame `map` |
| `/tf` | transforms received |
| `/move_base/GlobalPlanner/plan` | subscribed by `/paet_geometry_tokenizer` |

`rosnode info /paet_geometry_tokenizer` confirmed subscriptions to:

- `/map`
- `/move_base/GlobalPlanner/plan`
- `/scan_ira`
- `/tf`
- `/tf_static`

## Output Topic Validation

Topic types:

```text
/paet/events -> paet_ros/PAETEventArray
/paet/debug_markers -> visualization_msgs/MarkerArray
```

Publisher checks:

```text
/paet/events publisher: /paet_geometry_tokenizer
/paet/events subscriber: /paet_event_logger
/paet/debug_markers publisher: /paet_geometry_tokenizer
```

## Event Sample

`/paet/events` produced a real event during the validation run:

```text
token: doorway_narrow
confidence: 1.0
frame_id: map
spatial_anchor:
  x: 0.045526107389202514
  y: -0.033939789175066334
radius: 0.49784791469573975
evidence_channels:
  - scan
  - tf
  - robot_footprint
risk_delta: 1.0
wait_recommended: false
detour_recommended: true
reject_recommended: true
reason: observed_gap_width=0.996 required_width=1.000 clearance_margin=-0.004
```

`/paet/debug_markers` produced the corresponding marker:

```text
namespace: paet_events
type: SPHERE
frame_id: map
position:
  x: 0.04575856267701888
  y: -0.034237104489796735
scale:
  x: 0.9944030535289259
  y: 0.9944030535289259
  z: 0.2
color:
  r: 1.0
  g: 0.55
  b: 0.0
  a: 0.75
```

## Conclusion

The pulled `paet_ros` package built successfully in `/home/robot/catkin_ws`, launched with the robot navigation stack started by `ros_robot_control_mqtt`, and published both required PAET outputs:

- `/paet/events`
- `/paet/debug_markers`

The runtime produced a `doorway_narrow` event with scan, TF, and robot-footprint evidence, and produced the associated debug marker in the `map` frame.
