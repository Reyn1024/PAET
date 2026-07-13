# Prompt For Robot-Side Codex: Implement PAET ROS Package

Copy this prompt into the Codex session running on the Ubuntu robot.

```text
You are working on the Ubuntu robot machine for the PAET project.

Goal:
Implement and validate the ROS1 Noetic package `paet_ros` from the GitHub repository `https://github.com/Reyn1024/PAET.git`.

Important safety rules:
- Do not delete existing robot files.
- Do not modify production navigation packages such as move_base, TEB, Cartographer, chassis drivers, or zkwl_robot_start.
- Do not publish `/cmd_vel`, navigation goals, reset_pose, or actuator commands from PAET.
- Do not copy credentials, Wi-Fi data, private IPs, raw images, rosbag files, maps, shell history, SSH keys, or logs into the repository.
- Keep raw sensor data outside Git.
- Treat PAET V1 as a read-only sidecar package.

Tasks:
1. Pull the latest PAET repository from GitHub.
2. Keep the full PAET repository outside `/home/robot/catkin_ws/src` unless it is already there for a known reason. Recommended location: `/home/robot/PAET`.
3. Copy only `ros/paet_ros` into `/home/robot/catkin_ws/src/paet_ros`.
4. Run `chmod +x /home/robot/catkin_ws/src/paet_ros/scripts/*.py`.
5. Build with the robot's normal catkin build command.
6. Fix only package-local build/runtime errors in `paet_ros`.
7. Source the workspace.
8. Start the normal robot navigation stack if it is not already running.
9. Launch `roslaunch paet_ros paet_v1.launch`.
10. Verify these topics:
   - `/paet/events`
   - `/paet/debug_markers`
   - `/map`
   - `/scan` or `/scan_ira`
   - `/odom`
   - `/move_base/GlobalPlanner/plan`
11. Use RViz to inspect `/paet/debug_markers`.
12. Create a short sanitized validation report in:
    `04_experiments/paet_ros_robot_validation.md`

Validation report must include:
- Git commit tested.
- ROS distro and catkin workspace path.
- Whether `catkin_make` succeeded.
- Whether `roslaunch paet_ros paet_v1.launch` started.
- Topic availability table.
- Any errors or warnings.
- Whether any PAET events were emitted.
- Whether raw data was avoided.
- Next fixes needed.

Do not invent results. If a topic is missing or no event is emitted, say so directly.

After validation:
- Commit only source/config/report files.
- Do not commit raw data, bags, images, logs, credentials, or build directories.
- Push to GitHub.
```
