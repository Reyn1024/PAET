# paet_ros

ROS1 Noetic package for PAET V1 geometry-first event tokenization.

This package is designed as a read-only sidecar to the existing robot navigation stack. It publishes PAET events but does not command the robot.

## Build On Robot

```bash
cd ~
git clone https://github.com/Reyn1024/PAET.git PAET
cp -r ~/PAET/ros/paet_ros ~/catkin_ws/src/paet_ros
chmod +x ~/catkin_ws/src/paet_ros/scripts/*.py
cd ~/catkin_ws
catkin_make
source devel/setup.bash
```

If the robot already has the PAET repository cloned elsewhere, copy only `ros/paet_ros` into `~/catkin_ws/src/paet_ros`. Avoid cloning the full PAET repository inside `~/catkin_ws/src`, because catkin may discover duplicate packages.

## Run

Start the normal robot navigation stack first. Then:

```bash
roslaunch paet_ros paet_v1.launch
```

Use a unique `run_id` for each trial to avoid appending different trials into
the same log files:

```bash
roslaunch paet_ros paet_v1.launch run_id:=trial_$(date +%Y%m%d_%H%M%S)
```

Outputs:

- `/paet/events`
- `/paet/debug_markers`

Logs:

- `~/.ros/paet_logs/<run_id>_events.csv`
- `~/.ros/paet_logs/<run_id>_events.jsonl`

The logger writes one row per merged event segment. Repeated updates for the
same token are merged until the token has been absent for `logging.segment_gap_s`
seconds, so sustained detections do not appear as scan-rate duplicates.

Validate segment logging with synthetic events:

```bash
roscore
rosrun paet_ros paet_logger_segment_validation.py
```

## Safety

V1 is read-only:

- no `/cmd_vel` publication;
- no `move_base` goal publication;
- no map modification;
- no raw image logging.

## First Validation

```bash
rostopic echo /paet/events
rostopic hz /paet/events
rosrun rviz rviz
```

In RViz, add `MarkerArray` for `/paet/debug_markers`.
